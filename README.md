# AT_driver_manager
Modular automation engine that unifies **Playwright and Selenium** with concurrency, browser pooling, stealth, proxies, retries, and smart fallback
- Playwright = primary(default) engine: fast, stealthy, modern
- Selenium = only when explicitly requested: compatibility, legacy support
- Auto-installs Playwright browsers if missing
- Cleaner, maintainable code, easy to extend, debug
  - Stealth mode for Playwright pages
  - Optional proxy rotation
  - Retry decorator for robustness
  - Smart-ish fallback (Playwright → Selenium)
  - Context manager with proper cleanup

## Project Details
<details><summary>Project Structure/Architecture</summary>

```text
AT_driver_manager/          # Root of project
  archive/                 # store the archive files
  src/  
    driver_manager/
      __init__.py
      manager.py              ← main entry point
      playwright_engine.py    ← primary engine
      selenium_engine.py      ← secondary engine
      stealth.py              ← stealth mode helpers
      proxy_manager.py        ← proxy rotation
      retry.py                ← retry decorator
      auto_install.py         ← playwright browser installer
      
 requirements.txt
 .gitignore
 README.md
```
</details>
<details><summary>Playwright vs Selenium</summary>

- Using Playwright for:
  - scraping, automation, testing, CI/CD, Docker, stealth/anti-bot, reliability, speed.
- Using Selenium for: (is mostly legacy tech now)
  - need real Safari on macOS (not WebKit), need IE11 (legacy enterprise), must integrate with an old Selenium Grid 
</details>

<details><summary>Modules Details</summary>

- **manager.py (main entry point)**:
- **playwright_engine.py (primary engine)**:
- **selenium_engine.py (2nd engine)**:
- **Stealth.py (make me look human)** : navigator.webdriver, WebGL vendor, Canvas fingerprint, Timezone, Platform, Plugins, Languages, User‑agent, Headless mode
- **proxy_manager.py (auto rotate proxies)** : from a list, an API, a pool and per request and browser.
- **retry.py**:
- **auto_install.py**:
- **concurrency.py (async playwright)** : can run 10-100 page in parallel, make playwright becomes a monster.
- **browser_pool.py (reduces CPU load and speeds up)**: keep 5-20 playwright browsers open, reuse, rotate and close after N uses
- **retry.py** : use it on navigation, scraping and driver creation.
</details>

<details><summary>Modules/unit tests</summary>

All tests located /tests/
</details>

<details><summary>Automation Framework Layers</summary>

Current status: done 1-3 layers, in progress on layer 4, layer 5 TBD 
- Layer 1 (Engines): playwright and selenium
- Layer 2 (Enhances): stealth mode, proxy rotation, retry logic, auto-installers
- Layer 3 (Execution): single-page automation, multi-pages concurrency, browser pooling, and smart fallback.
- Layer 4 (Orchestration): config system, logging, metrics, error recovery, modular structure.
- Layer 5 (Dockerization): optional, TBD
</details>

## Ollama Library
Using driver_manager to scrape the information from [ollama library website](https://ollama.com/library). and generated a dataset.

<details><summary>Details</summary>

hybrid (fastest) version, runtime:30.1s
- Selenium : only for infinite scroll
- Requests: for /tags pages
- ThreadPoolExecutor: parlallel HTTP

Selenium only version, 

Enterprise-Grade version: Playwright concurrency engine version

scraper flow:
1. open library()
2. detect capabilities
3. get all models info
4. save data
5. close
</details>

## Section 508 Testing
Using driver_manager to scrape the information from [Section508.gov](https://www.section508.gov/test/?utm_source=copilot.com) 

<details><summary>Details</summary>

- dataset sample

</details>

## Other Info

<details><summary>Details</summary>
webddrivers
- Firefox → scraping, pooling, concurrency
- Chrome → JS‑heavy sites, CAPTCHAs, complex interactions
- Edge → fallback when Chrome/Firefox fail

Run test_all_browsers.py to check what browsers are available now.

Run auto_tuner.py will generate browser_benchmark.json, pick the best browser for you.
1. Browser startup time: how long does browser take to launch
2. Navigation time: how long take to load a given URL
3. DOM extraction time: how fast return elements
4. Infinite scroll performance: how many scroll cycles per second
5. Memory footprint: Which browser stays lighter under load?
6. Stability: Which browser crashes least under parallel load?


For tuner: can do more in future
- 🔹 Auto‑select engine (Requests vs Selenium vs Playwright)
- 🔹 Auto‑tune pool size (benchmark concurrency)
- 🔹 Auto‑tune scroll speed
- 🔹 Auto‑tune retry strategy
- 🔹 Auto‑tune parsing strategy

</details>