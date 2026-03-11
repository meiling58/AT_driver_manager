# driver_manager/stealth.py
# usage:
# from stealth import apply_stealth
# page = context.new_page()
# apply_stealth(page)


def apply_stealth(page):
    # Remove webdriver
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    """)

    # Fake plugins
    page.add_init_script("""
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4]
        });
    """)

    # Fake lanuages
    page.add_init_script("""
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
    """)

    # Fake WebGL vendor
    page.add_init_script("""
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter(param);
        };
    """)

    # Fake timezone
    page.add_init_script("""
        Intl.DateTimeFormat = function() {
            return { resolvedOptions: () => ({ timeZone: 'America/New_York' }) };
        };
    """)
