let body = document.body;
let profile = document.querySelector('.header .flex .profile');
let searchForm = document.querySelector('.header .flex .search-form');
let sideBar = document.querySelector('.side-bar');
let toggleBtn = document.querySelector('#toggle-btn');
let darkMode = localStorage.getItem('dark-mode');

if (document.querySelector('#user-btn')) {
   document.querySelector('#user-btn').onclick = () => {
      profile.classList.toggle('active');
      if (searchForm) searchForm.classList.remove('active');
   };
}

if (document.querySelector('#search-btn')) {
   document.querySelector('#search-btn').onclick = () => {
      searchForm.classList.toggle('active');
      if (profile) profile.classList.remove('active');
   };
}

if (document.querySelector('#menu-btn')) {
   document.querySelector('#menu-btn').onclick = () => {
      sideBar.classList.toggle('active');
      body.classList.toggle('active');
   };
}

if (document.querySelector('.side-bar .close-side-bar')) {
   document.querySelector('.side-bar .close-side-bar').onclick = () => {
      sideBar.classList.remove('active');
      body.classList.remove('active');
   };
}

window.onscroll = () => {
   if (profile) profile.classList.remove('active');
   if (searchForm) searchForm.classList.remove('active');
   if (window.innerWidth < 1200 && sideBar) {
      sideBar.classList.remove('active');
      body.classList.remove('active');
   }
};

const enableDarkMode = () => {
   if (toggleBtn) toggleBtn.classList.replace('fa-sun', 'fa-moon');
   body.classList.add('dark');
   localStorage.setItem('dark-mode', 'enabled');
};

const disableDarkMode = () => {
   if (toggleBtn) toggleBtn.classList.replace('fa-moon', 'fa-sun');
   body.classList.remove('dark');
   localStorage.setItem('dark-mode', 'disabled');
};

if (toggleBtn) {
   toggleBtn.onclick = () => {
      let dm = localStorage.getItem('dark-mode');
      if (dm === 'disabled' || !dm) {
         enableDarkMode();
      } else {
         disableDarkMode();
      }
   };
}

if (darkMode === 'enabled') {
   enableDarkMode();
}