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
    window.__testStep__ = (seconds, x, tacticalBoss=false) => {
      if(x !== undefined){targetX=x;game.x=x;}
      for(let i=0;i<seconds*20;i++){
        if(state!=="playing" && state!=="boss")break;
        if(state==="boss" && tacticalBoss){
          // Fire down the center unless a red marker locks that lane;
          // then move across the telegraphed artillery footprint.
          const desired=game.bossPhase===2
            ? (game.bossAim>=0?-2.85:2.85) : 0;
          targetX=desired;
          game.x=desired;
        }
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
        # Boss auto-fire is now an actual lane mechanic: it cannot deal
        # any damage from the outside railing and peaks at center.
        assert page.evaluate('__MBS_TEST__.bossAimFactor(0)') == 1
        assert page.evaluate('__MBS_TEST__.bossAimFactor(-3.05)') == 0
        assert 0 < page.evaluate('__MBS_TEST__.bossAimFactor(1.65)') < 1
        page.keyboard.press('p')
        assert page.evaluate('__MBS_TEST__.getState()') == 'paused'
        page.locator('[data-action="resume"]').click()
        assert page.evaluate('__MBS_TEST__.getState()') == 'playing'
        page.evaluate('__testStep__(45,-1.65,true)')
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
            page.evaluate('side => __testStep__(65, side, true)',side)
            outcomes.append(page.evaluate('__MBS_TEST__.getState()'))
        assert 'won' in outcomes, (level,outcomes)
    print('OK all 12 levels have at least one winning route with intentional boss aim/dodge')
    page.evaluate('__testStart__(1)')
    page.evaluate('__testStep__(20, -3.05)')
    assert page.evaluate('__MBS_TEST__.getState()') == 'boss', 'lane boss must start'
    before = page.evaluate('__MBS_TEST__.getSnapshot().bossHp')
    page.evaluate('__testStep__(0.8,-3.05)')
    assert page.evaluate('__MBS_TEST__.getSnapshot().bossHp') == before, 'outside lane must not damage boss'
    page.evaluate('__testStep__(0.8,0)')
    assert page.evaluate('__MBS_TEST__.getSnapshot().bossHp') < before, 'center firing must damage boss'
    print('OK boss requires center firing lane while leaving room to dodge')
    # Simulate the production edge JSON endpoint on the exact host. These are
    # browser-isolation tests, NOT proof of a live ShadowOps ID deployment.
    from json import dumps
    protected='https://bridgesquad.shadowops.dpdns.org'
    subject_a='123e4567-e89b-42d3-a456-426614174000'
    subject_b='123e4567-e89b-42d3-a456-426614174001'
    from time import time
    current={'sub':subject_a,'active':True,'token_status':200,'token_subject':None,
             'exchanges':0,'checks':0}
    profile=browser.new_page()
    profile.route(protected+'/', lambda route: route.fulfill(status=200,body=HTML,content_type='text/html'))
    def identity_route(route):
        is_exchange=route.request.method=='POST'
        if not current['active']:
            route.fulfill(status=401,body='{"error":"authentication_required"}',content_type='application/json')
        elif is_exchange:
            body=route.request.post_data_json
            assert body=={'token':'synthetic-ephemeral-test-token'}
            assert route.request.headers.get('origin')==protected
            current['exchanges']+=1
            sub=current['token_subject'] or current['sub']
            route.fulfill(status=200,body=dumps({'identity':'bridgesquad','subject':sub,
                 'expires_at':int(time())+118}),content_type='application/json')
        else:
            current['checks']+=1
            route.fulfill(status=200,body=dumps({'identity':'bridgesquad',
                 'subject':current['sub'],'expires_at':int(time())+70}),
                 content_type='application/json')
    profile.route(protected+'/api/bridgesquad/session', identity_route)
    cors={'Access-Control-Allow-Origin':protected,'Access-Control-Allow-Credentials':'true',
          'Access-Control-Allow-Headers':'Content-Type','Access-Control-Allow-Methods':'POST, OPTIONS'}
    def token_route(route):
        if route.request.method=='OPTIONS':
            route.fulfill(status=204,headers=cors)
        elif current['token_status']!=200:
            route.fulfill(status=current['token_status'],headers=cors,
                          body='{"error":"authentication_required"}',content_type='application/json')
        else:
            route.fulfill(status=200,headers=cors,
                          body='{"token":"synthetic-ephemeral-test-token"}',content_type='application/json')
    profile.route('https://id.shadowops.dpdns.org/api/identity/token',token_route)
    profile.goto(protected+'/')
    profile.wait_for_function("window.__MBS_TEST__ && __MBS_TEST__.getState()==='menu'")
    profile.evaluate("(s) => localStorage.setItem('shadowops.mbs.progress.v1:'+s,JSON.stringify({unlocked:9,stars:[3],wins:8}))",subject_a)
    profile.reload()
    profile.wait_for_function("window.__MBS_TEST__ && __MBS_TEST__.getProgress().unlocked===9")
    current['sub']=subject_b
    profile.reload()
    profile.wait_for_function("window.__MBS_TEST__ && __MBS_TEST__.getState()==='menu'")
    assert profile.evaluate('__MBS_TEST__.getProgress().unlocked') == 1, 'another account must not inherit progress'
    current['sub']=subject_a
    profile.reload()
    profile.wait_for_function("window.__MBS_TEST__ && __MBS_TEST__.getProgress().unlocked===9")
    # A short-lived edge cookie must renew seamlessly without navigating or
    # restarting the active level. IdP returns a transient bearer token; only
    # the new HttpOnly Worker cookie persists (the browser script never saves JWTs).
    profile.locator('[data-action="play"]').click()
    assert profile.evaluate('__MBS_TEST__.getState()')=='playing'
    old_exp=profile.evaluate('__MBS_TEST__.getIdentity().expiresAt')
    profile.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    profile.wait_for_function("(previous) => __MBS_TEST__.getIdentity().expiresAt > previous",arg=old_exp)
    assert profile.evaluate('__MBS_TEST__.getState()')=='playing'
    assert current['exchanges']>=1
    assert profile.evaluate("Object.keys(localStorage).filter(k=>k.includes('token')||k.includes('jwt'))")==[]
    print('OK production session renews from ShadowOps ID without losing the active level')

    # A signed-in IdP switching subjects during renewal must NOT migrate,
    # overwrite or reuse the previous account's campaign.
    current['token_subject']=subject_b
    profile.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    profile.wait_for_function("__MBS_TEST__.getState()==='auth-blocked'")
    assert not profile.evaluate('__MBS_TEST__.getIdentity().verified')
    assert profile.evaluate("(sub) => JSON.parse(localStorage.getItem('shadowops.mbs.progress.v1:'+sub)).unlocked",subject_a)==9
    print('OK changed account during renewal locks old campaign without save crossover')

    # An explicitly revoked IdP session must lock the currently open game,
    # not just protect the next HTML navigation.
    current['token_subject']=None
    current['sub']=subject_a
    profile.reload()
    profile.wait_for_function("__MBS_TEST__.getState()==='menu'")
    current['token_status']=401
    profile.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    profile.wait_for_function("__MBS_TEST__.getState()==='auth-blocked'")
    current['token_status']=200

    current['active']=False
    profile.reload()
    profile.wait_for_function("window.__MBS_TEST__ && __MBS_TEST__.getState()==='auth-blocked'")
    print('OK production bootstrap, renewal, account isolation and revoked-session lock')
    profile.close()
    browser.close()
