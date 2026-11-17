"""Browser smoke test. Requires `pip install playwright` and Chromium installed."""
from pathlib import Path
from shutil import which
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
# The deterministic stepper exists only in the in-memory test page, not in the game.
TEST_HTML = HTML.replace(
    'mainMenu();requestAnimationFrame(frame);',
    '''mainMenu();
    window.__testStart__ = n => start(n);
    window.__testStep__ = (seconds, x) => {
      if(x !== undefined){targetX=x;game.x=x;}
      for(let i=0;i<seconds*20;i++){
        if(state!=="playing" && state!=="boss")break;
        t+=.05;update(.05);
      }
    };
    requestAnimationFrame(frame);'''
)

with sync_playwright() as p:
    browser_args = {'headless': True, 'args': ['--no-sandbox']}
    if which('chromium'):
        browser_args['executable_path'] = which('chromium')
    browser = p.chromium.launch(**browser_args)
    for width,height in [(1440,900),(390,844)]:
        page = browser.new_page(viewport={'width':width,'height':height})
        errors=[]
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content(TEST_HTML)
        assert page.title() == 'Matthias Bridge Squad — ShadowOps'
        assert page.evaluate('__MBS_TEST__.getState()') == 'menu'
        page.locator('[data-action="levels"]').click()
        assert page.locator('button.level').count() == 12
        assert page.locator('button.level:not([disabled])').count() == 1
        page.locator('[data-action="play"]').click()
        assert page.evaluate('__MBS_TEST__.getState()') == 'playing'
        # Pointer coordinates must map to the leader's projected position,
        # on both narrow phones and wide desktop viewports.
        projected_scale = min(width * .115, height * .145) / (1 + 5.5 * .042)
        page.mouse.move(width / 2 + projected_scale * 1.65, height * .75)
        page.evaluate('__testStep__(1)')
        assert abs(page.evaluate('__MBS_TEST__.getSnapshot().x') - 1.65) < .03
        # The mathematical forecast must use the exact gameplay operation.
        assert page.evaluate('__MBS_TEST__.gateOutcome(7, {op:"+", n:11})') == 18
        assert page.evaluate('__MBS_TEST__.gateOutcome(7, {op:"×", n:2})') == 14
        assert page.evaluate('__MBS_TEST__.gateOutcome(110, {op:"×", n:3})') == 120
        assert page.evaluate('__MBS_TEST__.gateOutcome(9, {op:"÷", n:2})') == 4
        assert page.evaluate('__MBS_TEST__.gateOutcome(9, {op:"−", n:99})') == 1
        page.keyboard.press('p')
        assert page.evaluate('__MBS_TEST__.getState()') == 'paused'
        page.locator('[data-action="resume"]').click()
        assert page.evaluate('__MBS_TEST__.getState()') == 'playing'
        page.evaluate('__testStep__(45,-1.65)')
        assert page.evaluate('__MBS_TEST__.getState()') == 'won'
        assert page.evaluate('__MBS_TEST__.getProgress().unlocked') == 2
        assert page.evaluate('__MBS_TEST__.getProgress().stars[0]') == 3
        page.locator('[data-action="next"]').click()
        assert page.evaluate('__MBS_TEST__.getSnapshot().level') == 2
        assert not errors, errors
        page.close()
        print('OK viewport', width, height, 'campaign unlock, 3-star victory, pause, navigation')
    page=browser.new_page()
    page.set_content(TEST_HTML)
    for level in range(1,13):
        outcomes=[]
        for side in (-1.65,1.65):
            page.evaluate('n => __testStart__(n)',level)
            page.evaluate('side => __testStep__(65, side)',side)
            outcomes.append(page.evaluate('__MBS_TEST__.getState()'))
        assert 'won' in outcomes, (level,outcomes)
    print('OK all 12 levels have at least one winning route on a fixed lane')
    browser.close()
