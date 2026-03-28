/*
 * Ruuz Context Engine v0.2
 * Adapts storefront content based on real-time weather + time of day
 */

(function () {
  'use strict';

  var CONFIG = {
    apiKey: 'YOUR_OPENWEATHERMAP_API_KEY',
    defaultLat: 38.9072,
    defaultLon: -77.0369,
    heroImages: {
      sunny: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/ruuz-hero-sunny.jpg?v=1774656230',
      rainy: 'https://cdn.shopify.com/s/files/1/0988/6964/1498/files/ruuz-hero-rainy.jpg?v=1774656099'
    },
    moods: {
      sunny: {
        morning: {
          headline: 'Start Your Morning Strong',
          subheadline: 'Lightweight gear to power your sunrise session'
        },
        afternoon: {
          headline: 'Crush Your Afternoon Session',
          subheadline: 'Breathable layers for peak-heat training'
        },
        evening: {
          headline: 'End the Day Right',
          subheadline: 'Comfortable fits for your sunset cooldown'
        },
        buttonText: 'Shop Sunshine Picks',
        buttonLink: '/collections/sunshine-picks',
        heroColor: '#FFFFFF',
        buttonBg: '#FFFFFF',
        buttonColor: '#2C2C2C'
      },
      rainy: {
        morning: {
          headline: 'Own the Morning Storm',
          subheadline: 'Waterproof layers to start the day right'
        },
        afternoon: {
          headline: 'Train Through the Rain',
          subheadline: 'Stay dry and focused all afternoon'
        },
        evening: {
          headline: 'Brave the Evening Downpour',
          subheadline: 'Reflective, waterproof gear for after-dark runs'
        },
        buttonText: 'Shop Rainy Day Essentials',
        buttonLink: '/collections/rainy-day-essentials',
        heroColor: '#FFFFFF',
        buttonBg: '#FFFFFF',
        buttonColor: '#1A2A3A'
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

  function applyMood(mood) {
    var timeOfDay = getTimeOfDay();
    var moodConfig = CONFIG.moods[mood];
    var timeConfig = moodConfig[timeOfDay];

    document.body.setAttribute('data-ruuz-mood', mood);
    document.body.setAttribute('data-ruuz-time', timeOfDay);

    var sunnySection = document.getElementById('ruuz-sunny');
    var rainySection = document.getElementById('ruuz-rainy');

    if (mood === 'rainy') {
      if (sunnySection) sunnySection.style.display = 'none';
      if (rainySection) rainySection.style.display = '';
    } else {
      if (sunnySection) sunnySection.style.display = '';
      if (rainySection) rainySection.style.display = 'none';
    }

    var hero = document.querySelector('.ruuz-hero');
    var heading = document.querySelector('.ruuz-hero-heading');
    var subheading = document.querySelector('.ruuz-hero-subheading');
    var button = document.querySelector('.ruuz-hero-button');

    if (hero) {
      hero.style.backgroundImage = 'url(' + CONFIG.heroImages[mood] + ')';
      hero.style.color = moodConfig.heroColor;
    }
    if (heading) heading.textContent = timeConfig.headline;
    if (subheading) subheading.textContent = timeConfig.subheadline;
    if (button) {
      button.textContent = moodConfig.buttonText;
      button.href = moodConfig.buttonLink;
      button.style.backgroundColor = moodConfig.buttonBg;
      button.style.color = moodConfig.buttonColor;
    }

    console.log('[Ruuz] Mood: ' + mood + ' | Time: ' + timeOfDay + ' | Headline: ' + timeConfig.headline);
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

  function init() {
    console.log('[Ruuz] Context Engine v0.2 starting...');

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        function (pos) {
          console.log('[Ruuz] Location detected');
          fetchWeather(pos.coords.latitude, pos.coords.longitude);
        },
        function () {
          console.log('[Ruuz] Location denied, using default (DC)');
          fetchWeather(CONFIG.defaultLat, CONFIG.defaultLon);
        }
      );
    } else {
      fetchWeather(CONFIG.defaultLat, CONFIG.defaultLon);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
