/*
 * Ruuz Context Engine v1.1 (Vercel Proxy Integration)
 * Calls Vercel serverless proxy which forwards to FastAPI backend on Railway
 * Proxy: https://ruuz.vercel.app/api/context
 * Keeps API key server-side only
 */

(function () {
  'use strict';

  var BACKEND_URL = 'https://ruuz.vercel.app';
  var DEFAULT_LAT = 38.9072;
  var DEFAULT_LON = -77.0369;
  var DEFAULT_COUNTRY = 'US';

  var IMAGES = {
    sunny: {
      hero: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/The_sunny_hero_image.jpg?v=1774908302',
      media1: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/sunny_day1.jpg?v=1774898045',
      media2: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/sunny_day_2.png?v=1774908442'
    },
    rainy: {
      hero: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/The_rainy_hero_image.jpg?v=1774908322',
      media1: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/rainy_day_1.png?v=1774908455',
      media2: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/rainy_day_2.jpg?v=1774908558'
    }
  };

  var BUTTONS = {
    sunny: { text: 'Shop Sunshine Picks', link: '/collections/sunshine-picks' },
    rainy: { text: 'Shop Rainy Day Essentials', link: '/collections/rainy-day-essentials' }
  };

  function createHeroButton(text, link) {
    var button = document.createElement('a');
    button.id = 'ruuz-hero-button';
    button.href = link;
    button.textContent = text;
    button.style.cssText = 'display: inline-block; padding: 14px 32px; font-size: 1rem; font-weight: 600; text-decoration: none; border-radius: 4px; background-color: #FFFFFF; color: #2C2C2C; margin-top: 20px; transition: opacity 0.3s ease; cursor: pointer;';
    button.addEventListener('mouseenter', function () { button.style.opacity = '0.85'; });
    button.addEventListener('mouseleave', function () { button.style.opacity = '1'; });
    return button;
  }

  function swapAllImages(container, newSrc) {
    if (!container) return;
    var imgs = container.querySelectorAll('img');
    for (var i = 0; i < imgs.length; i++) {
      imgs[i].src = newSrc;
      imgs[i].srcset = '';
    }
  }

  function applyContext(data) {
    var mood = data.mood;
    var ai = data.ai_copy || {};
    var images = IMAGES[mood];
    var btn = BUTTONS[mood];
    var alerts = data.alerts || [];

    document.body.setAttribute('data-ruuz-mood', mood);
    document.body.setAttribute('data-ruuz-time', data.time_of_day);
    document.body.setAttribute('data-ruuz-daylight', data.daylight);

    // 1. ANNOUNCEMENT BANNER
    var announcementText = ai.announcement || alerts.join(' | ') || 'Welcome to our store';
    if (alerts.length > 0) {
      announcementText = alerts.join(' | ');
    }
    var announcements = document.querySelectorAll('.announcement-bar__text');
    for (var i = 0; i < announcements.length; i++) {
      announcements[i].textContent = announcementText;
    }

    // 2. HERO
    var heroContainer = document.querySelector('.hero__container');
    if (heroContainer) {
      var heroHeading = heroContainer.querySelector('h1');
      if (heroHeading && ai.headline) heroHeading.textContent = ai.headline;

      var heroSubtext = heroContainer.querySelector('rte-formatter p');
      if (heroSubtext && ai.subheadline) heroSubtext.textContent = ai.subheadline;

      var heroImage = heroContainer.querySelector('img.hero__media');
      if (heroImage) {
        heroImage.src = images.hero;
        heroImage.srcset = '';
      }

      var existingButton = document.getElementById('ruuz-hero-button');
      if (existingButton) {
        existingButton.textContent = btn.text;
        existingButton.href = btn.link;
      } else {
        var heroContent = heroContainer.querySelector('.hero__content-wrapper');
        if (heroContent) {
          heroContent.appendChild(createHeroButton(btn.text, btn.link));
        }
      }
    }

    // 3. COLLECTIONS
    var sunnyGrid = document.querySelector('[id*="product_list_themegen"]');
    var rainySection = document.getElementById('ruuz-rainy');
    if (mood === 'rainy') {
      if (sunnyGrid) sunnyGrid.style.display = 'none';
      if (rainySection) rainySection.style.display = '';
    } else {
      if (sunnyGrid) sunnyGrid.style.display = '';
      if (rainySection) rainySection.style.display = 'none';
    }

    // 4. HIDE "Our shop" AND FIX SPACING
    var ourShopBlock = document.querySelector('[class*="text_pH8qby"]');
    if (ourShopBlock) ourShopBlock.style.display = 'none';

    var pullQuoteSection = document.querySelector('[id*="section_x8mrnx"]');
    if (pullQuoteSection) {
      pullQuoteSection.style.paddingTop = '0px';
      pullQuoteSection.style.marginTop = '0px';
      var pullQuoteContent = pullQuoteSection.querySelector('.section-content-wrapper');
      if (pullQuoteContent) {
        pullQuoteContent.style.setProperty('--padding-block-start', '20px');
      }
    }

    // 5. PULL QUOTE
    if (pullQuoteSection && ai.pull_quote) {
      var allH2s = pullQuoteSection.querySelectorAll('h2');
      for (var j = 0; j < allH2s.length; j++) {
        if (allH2s[j].textContent.length > 30) {
          allH2s[j].textContent = ai.pull_quote;
          break;
        }
      }
    }

    // 6. MEDIA SECTION 1
    var mediaSection1 = document.querySelector('[id*="media_with_content_xMM9EF"]');
    if (mediaSection1) {
      var heading1 = mediaSection1.querySelector('h2');
      if (heading1 && ai.media1_heading) heading1.textContent = ai.media1_heading;

      var texts1 = mediaSection1.querySelectorAll('rte-formatter p, .rte p');
      if (texts1.length > 0 && ai.media1_text) texts1[0].textContent = ai.media1_text;

      swapAllImages(mediaSection1, images.media1);
      var btn1 = mediaSection1.querySelector('a.button, a[class*="button"]');
      if (btn1) btn1.href = btn.link;
    }

    // 7. MEDIA SECTION 2
    var mediaSection2 = document.querySelector('[id*="media_with_content_nrnzPh"]');
    if (mediaSection2) {
      var heading2 = mediaSection2.querySelector('h2');
      if (heading2 && ai.media2_heading) heading2.textContent = ai.media2_heading;

      var texts2 = mediaSection2.querySelectorAll('rte-formatter p, .rte p');
      if (texts2.length > 0 && ai.media2_text) texts2[0].textContent = ai.media2_text;

      swapAllImages(mediaSection2, images.media2);
      var btn2 = mediaSection2.querySelector('a.button, a[class*="button"]');
      if (btn2) btn2.href = btn.link;
    }

    console.log('[Ruuz] ---- Live Backend Context ----');
    console.log('[Ruuz] Mood: ' + mood + ' | Time: ' + data.time_of_day);
    console.log('[Ruuz] Weather: ' + data.weather.description + ' ' + data.weather.temp + 'F');
    console.log('[Ruuz] AI Headline: ' + (ai.headline || 'fallback'));
    console.log('[Ruuz] AI Subheadline: ' + (ai.subheadline || 'fallback'));
    console.log('[Ruuz] AI Announcement: ' + (ai.announcement || 'fallback'));
    console.log('[Ruuz] AI Pull Quote: ' + (ai.pull_quote || 'fallback'));
    console.log('[Ruuz] AI Media 1: ' + (ai.media1_heading || 'fallback') + ' / ' + (ai.media1_text || 'fallback'));
    console.log('[Ruuz] AI Media 2: ' + (ai.media2_heading || 'fallback') + ' / ' + (ai.media2_text || 'fallback'));
    console.log('[Ruuz] AI Ribbon: ' + (ai.ribbon || 'fallback'));
    console.log('[Ruuz] Alerts: ' + alerts.join(' | '));
    console.log('[Ruuz] News: ' + (data.news.top_headline || 'none'));
    console.log('[Ruuz] Stock: ' + data.stock_market.sentiment + ' (' + data.stock_market.change_percent + '%)');
    console.log('[Ruuz] -------------------------------');
  
    // 8. MARQUEE (live data ticker — 6 different signals)
    var marquee = document.querySelector('marquee-component');
    if (marquee) {
      var tickerMessages = [
        ai.ribbon || 'Empowering women to move freely and confidently',
        data.weather.temp + '°F ' + data.weather.description,
        'UV Index ' + data.uv.index + ' (' + data.uv.alert + ')',
        'Air Quality: ' + data.air_quality.label + ' (' + data.air_quality.index + '/5)',
        data.news.top_headline ? data.news.top_headline + ' — ' + data.news.source : 'Stay informed, stay active',
        'Market: S&P 500 ' + data.stock_market.sentiment + ' (' + data.stock_market.change_percent + '%)'
      ];

      var marqueeTexts = marquee.querySelectorAll('.text-block p');
      for (var m = 0; m < marqueeTexts.length; m++) {
        marqueeTexts[m].textContent = tickerMessages[m % tickerMessages.length];
      }
    }
  }
  
  function callBackend(lat, lon, country) {
    var url = BACKEND_URL + '/api/context?lat=' + lat + '&lon=' + lon + '&country=' + country;
    console.log('[Ruuz] Calling backend: ' + url);

    fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        console.log('[Ruuz] Backend response received');
        applyContext(data);
      })
      .catch(function (err) {
        console.log('[Ruuz] Backend error: ' + err);
      });
  }

  function fetchIPLocation() {
    fetch('https://ipapi.co/json/')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.latitude && data.longitude) {
          console.log('[Ruuz] IP location: ' + data.city + ', ' + data.country_code);
          callBackend(data.latitude, data.longitude, data.country_code || DEFAULT_COUNTRY);
        } else {
          callBackend(DEFAULT_LAT, DEFAULT_LON, DEFAULT_COUNTRY);
        }
      })
      .catch(function () {
        callBackend(DEFAULT_LAT, DEFAULT_LON, DEFAULT_COUNTRY);
      });
  }

  function init() {
    console.log('[Ruuz] Context Engine v1.0 (Live Backend) starting...');

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          console.log('[Ruuz] Browser location detected');
          callBackend(pos.coords.latitude, pos.coords.longitude, DEFAULT_COUNTRY);
        },
        function () {
          console.log('[Ruuz] Browser denied, using IP location...');
          fetchIPLocation();
        }
      );
    } else {
      fetchIPLocation();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
