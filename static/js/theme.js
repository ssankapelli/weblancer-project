const themeSwitch = document.getElementById('themeSwitch');
const preferredTheme = localStorage.getItem('theme');

if (themeSwitch) {
  if (preferredTheme === 'dark') {
    themeSwitch.checked = true;
    document.documentElement.setAttribute('data-bs-theme', 'dark');
  } else {
    themeSwitch.checked = false;
    document.documentElement.removeAttribute('data-bs-theme');
  }

  themeSwitch.addEventListener('change', function() {
    if (themeSwitch.checked) {
      document.documentElement.setAttribute('data-bs-theme', 'dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.removeAttribute('data-bs-theme');
      localStorage.setItem('theme', 'light');
    }
  });
}

function makeNavElementActive(elementId) {
	const navActiveElement = document.getElementById(elementId);
	  console.log("hmm");
	if (navActiveElement) {
	  navActiveElement.classList.add("active");
	  console.log(navActiveElement);
	  console.log("hmm2");
	}
}