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
