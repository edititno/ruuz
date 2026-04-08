/*
* Ruuz Context Engine v0.5 (Rebel Theme - Full Integration)
* Adapts: banner, hero, collections, pull quote, media sections
 */

(function () {
  'use strict';

  var CONFIG = {
    apiKey: 'YOUR_OPENWEATHERMAP_API_KEY',
    defaultLat: 38.9072,
    defaultLon: -77.0369,

    images: {
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
    },

    moods: {
      sunny: {
        buttonText: 'Shop Sunshine Picks',
        buttonLink: '/collections/sunshine-picks',
        morning: {
          headline: 'Start Your Morning Strong',
          subheadline: 'Lightweight gear to power your sunrise session',
          announcement: 'Perfect morning for an outdoor run — shop sun-ready gear',
          pullQuote: 'When the sun is out, so are we. Gear built for women who train without limits.',
          media1Heading: 'Superior Comfort',
          media1Text: 'Breathable fabrics that keep you cool and dry through your morning workout.',
          media2Heading: 'Performance Redefined',
          media2Text: 'Lightweight layers designed to flex, stretch, and move with every rep.'
        },
        afternoon: {
          headline: 'Crush Your Afternoon Session',
          subheadline: 'Breathable layers for peak-heat training',
          announcement: 'It\'s warm out there — stay cool with our lightweight picks',
          pullQuote: 'Afternoon heat calls for breathable, sweat-wicking gear designed to move with you.',
          media1Heading: 'Beat the Heat',
          media1Text: 'Ultra-light moisture-wicking fabrics that keep you cool when the temperature climbs.',
          media2Heading: 'Built to Perform',
          media2Text: 'From HIIT to hot yoga, our activewear handles the heat so you can focus on your goals.'
        },
        evening: {
          headline: 'End the Day Right',
          subheadline: 'Comfortable fits for your sunset cooldown',
          announcement: 'Beautiful evening ahead — gear up for a sunset session',
          pullQuote: 'Wind down your day with comfortable performance wear that transitions from workout to life.',
          media1Heading: 'Sunset Ready',
          media1Text: 'Comfortable fits that take you from your evening run to dinner without missing a beat.',
          media2Heading: 'Effortless Style',
          media2Text: 'Performance wear that looks as good after the workout as it does during. No compromises.'
        }
      },
      rainy: {
        buttonText: 'Shop Rainy Day Essentials',
        buttonLink: '/collections/rainy-day-essentials',
        morning: {
          headline: 'Own the Morning Storm',
          subheadline: 'Waterproof layers to start the day right',
          announcement: 'Rain today — stay dry with our waterproof collection',
          pullQuote: 'Rain doesn\'t cancel training. Our waterproof layers keep you moving through any forecast.',
          media1Heading: 'Storm Protection',
          media1Text: 'Sealed seams and waterproof shells that block the rain without trapping heat.',
          media2Heading: 'Grip and Go',
          media2Text: 'Wet weather demands gear that stays put. No slipping, no soaking, no excuses.'
        },
        afternoon: {
          headline: 'Train Through the Rain',
          subheadline: 'Stay dry and focused all afternoon',
          announcement: 'Wet weather outside — shop rainy day essentials',
          pullQuote: 'Built for women who don\'t check the weather before they train. Waterproof. Windproof. Unstoppable.',
          media1Heading: 'Stay Dry, Stay Moving',
          media1Text: 'Water-resistant layers that let you push through afternoon downpours without slowing down.',
          media2Heading: 'All-Weather Training',
          media2Text: 'Our activewear is tested in the worst conditions so you can perform at your best in any weather.'
        },
        evening: {
          headline: 'Brave the Evening Downpour',
          subheadline: 'Reflective, waterproof gear for after-dark runs',
          announcement: 'Rainy night? Stay visible with reflective waterproof gear',
          pullQuote: 'When the sky goes dark and wet, our reflective waterproof gear keeps you safe and dry.',
          media1Heading: 'Reflective Protection',
          media1Text: 'High-visibility details and waterproof construction for safe after-dark training.',
          media2Heading: 'Night-Ready Layers',
          media2Text: 'Insulated, waterproof, and reflective. Everything you need to own the rainy night.'
        }
      }
    }
  };

  function getTimeOfDay() {
    var hour = new Date().getHours();
    if (hour >= 5 && hour < 12) return 'morning';
    if (hour >= 12 && hour < 17) return 'afternoon';
    return 'evening';
  }

  function getMood(weatherCode) {
    if (weatherCode === 800 || weatherCode === 801 || weatherCode === 802) {
      return 'sunny';
    }
    return 'rainy';
  }

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

  function applyMood(mood) {
    var timeOfDay = getTimeOfDay();
    var moodConfig = CONFIG.moods[mood];
    var timeConfig = moodConfig[timeOfDay];
    var moodImages = CONFIG.images[mood];

    document.body.setAttribute('data-ruuz-mood', mood);
    document.body.setAttribute('data-ruuz-time', timeOfDay);

    // 1. ANNOUNCEMENT BANNER
    var announcements = document.querySelectorAll('.announcement-bar__text');
    for (var i = 0; i < announcements.length; i++) {
      announcements[i].textContent = timeConfig.announcement;
    }
    console.log('[Ruuz] Announcement updated');

    // 2. HERO
    var heroContainer = document.querySelector('.hero__container');
    if (heroContainer) {
      var heroHeading = heroContainer.querySelector('h1');
      if (heroHeading) heroHeading.textContent = timeConfig.headline;

      var heroSubtext = heroContainer.querySelector('rte-formatter p');
      if (heroSubtext) heroSubtext.textContent = timeConfig.subheadline;

      var heroImage = heroContainer.querySelector('img.hero__media');
      if (heroImage) {
        heroImage.src = moodImages.hero;
        heroImage.srcset = '';
      }

      var existingButton = document.getElementById('ruuz-hero-button');
      if (existingButton) {
        existingButton.textContent = moodConfig.buttonText;
        existingButton.href = moodConfig.buttonLink;
      } else {
        var heroContent = heroContainer.querySelector('.hero__content-wrapper');
        if (heroContent) {
          heroContent.appendChild(createHeroButton(moodConfig.buttonText, moodConfig.buttonLink));
        }
      }
      console.log('[Ruuz] Hero updated');
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
    console.log('[Ruuz] Collections swapped');

    // 4. HIDE "Our shop" AND FIX WHITE SPACE
    var ourShopBlock = document.querySelector('[class*="text_pH8qby"]');
    if (ourShopBlock) {
      ourShopBlock.style.display = 'none';
    }

    var pullQuoteSection = document.querySelector('[id*="section_x8mrnx"]');
    if (pullQuoteSection) {
      pullQuoteSection.style.paddingTop = '0px';
      pullQuoteSection.style.marginTop = '0px';
      var pullQuoteContent = pullQuoteSection.querySelector('.section-content-wrapper');
      if (pullQuoteContent) {
        pullQuoteContent.style.setProperty('--padding-block-start', '20px');
      }
    }
    console.log('[Ruuz] Our shop hidden, spacing fixed');

    // 5. PULL QUOTE TEXT
    if (pullQuoteSection) {
      var allH2s = pullQuoteSection.querySelectorAll('h2');
      for (var j = 0; j < allH2s.length; j++) {
        if (allH2s[j].textContent.length > 30) {
          allH2s[j].textContent = timeConfig.pullQuote;
          console.log('[Ruuz] Pull quote updated');
          break;
        }
      }
    }

    // 6. MEDIA WITH TEXT - SECTION 1 (left image)
    var mediaSection1 = document.querySelector('[id*="media_with_content_xMM9EF"]');
    if (mediaSection1) {
      var heading1 = mediaSection1.querySelector('h2');
      if (heading1) heading1.textContent = timeConfig.media1Heading;

      var texts1 = mediaSection1.querySelectorAll('rte-formatter p, .rte p');
      if (texts1.length > 0) texts1[0].textContent = timeConfig.media1Text;

      swapAllImages(mediaSection1, moodImages.media1);

      var btn1 = mediaSection1.querySelector('a.button, a[class*="button"]');
      if (btn1) {
        btn1.href = moodConfig.buttonLink;
      }
      console.log('[Ruuz] Media section 1 updated');
    }

    // 7. MEDIA WITH TEXT - SECTION 2 (right image)
    var mediaSection2 = document.querySelector('[id*="media_with_content_nrnzPh"]');
    if (mediaSection2) {
      var heading2 = mediaSection2.querySelector('h2');
      if (heading2) heading2.textContent = timeConfig.media2Heading;

      var texts2 = mediaSection2.querySelectorAll('rte-formatter p, .rte p');
      if (texts2.length > 0) texts2[0].textContent = timeConfig.media2Text;

      swapAllImages(mediaSection2, moodImages.media2);

      var btn2 = mediaSection2.querySelector('a.button, a[class*="button"]');
      if (btn2) {
        btn2.href = moodConfig.buttonLink;
      }
      console.log('[Ruuz] Media section 2 updated');
    }

    // FULL LOG
    console.log('[Ruuz] ---- Context Applied ----');
    console.log('[Ruuz] Mood: ' + mood + ' | Time: ' + timeOfDay);
    console.log('[Ruuz] Headline: ' + timeConfig.headline);
    console.log('[Ruuz] Announcement: ' + timeConfig.announcement);
    console.log('[Ruuz] Pull quote: ' + timeConfig.pullQuote);
    console.log('[Ruuz] Media 1: ' + timeConfig.media1Heading);
    console.log('[Ruuz] Media 2: ' + timeConfig.media2Heading);
    console.log('[Ruuz] Collection: ' + (mood === 'rainy' ? 'Rainy Day Essentials' : 'Sunshine Picks'));
    console.log('[Ruuz] --------------------------');
  }

  function fetchWeather(lat, lon) {
    var url = 'https://api.openweathermap.org/data/2.5/weather?lat=' + lat + '&lon=' + lon + '&appid=' + CONFIG.apiKey + '&units=imperial';

    fetch(url)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.weather && data.weather[0]) {
          var code = data.weather[0].id;
          var mood = getMood(code);
          console.log('[Ruuz] Weather: ' + data.weather[0].description + ' | Code: ' + code + ' | Mood: ' + mood + ' | Temp: ' + data.main.temp + 'F');
          applyMood(mood);
        }
      })
      .catch(function () {
        console.log('[Ruuz] API error, defaulting to sunny');
        applyMood('sunny');
      });
  }

  function fetchIPLocation() {
    fetch('https://ipapi.co/json/')
      .then(function (res) { return res.json(); })
      .then(function (data) {
        if (data.latitude && data.longitude) {
          console.log('[Ruuz] IP location detected: ' + data.city + ', ' + data.region);
          fetchWeather(data.latitude, data.longitude);
        } else {
          console.log('[Ruuz] IP location failed, using default (DC)');
          fetchWeather(CONFIG.defaultLat, CONFIG.defaultLon);
        }
      })
      .catch(function () {
        console.log('[Ruuz] IP location error, using default (DC)');
        fetchWeather(CONFIG.defaultLat, CONFIG.defaultLon);
      });
  }

  function init() {
    console.log('[Ruuz] Context Engine v0.5 starting...');

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          console.log('[Ruuz] Browser location detected');
          fetchWeather(pos.coords.latitude, pos.coords.longitude);
        },
        function () {
          console.log('[Ruuz] Browser location denied, trying IP location...');
          fetchIPLocation();
        }
      );
    } else {
      console.log('[Ruuz] Geolocation not supported, trying IP location...');
      fetchIPLocation();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
