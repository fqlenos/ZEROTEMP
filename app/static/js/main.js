// Script for NavBar to be automatically set to "Active" 
// Witing for page to be fully ready otherwise it will not be executed
document.addEventListener("DOMContentLoaded", function() {
  var navLinks = document.querySelectorAll(".nav-item .nav-link");
  var currentUrl = window.location.href;
  navLinks.forEach(function (link) {
    if (link.href === currentUrl) {
      link.parentElement.classList.add("active");
    }
  });
});

// Script for go-back
document.addEventListener("DOMContentLoaded", function() {
  let back_btn = document.getElementById("back-to-previous-page");
  if (back_btn !== null) {
    back_btn.onclick = function() {
      history.back();
    };
  }
});

// Script for toggleing the Challenges Table
$(document).ready(function() {
  $('tr[data-target]').click(function() {
      var target = $(this).data('target');
      $(target).toggle();
  });
});

// Script for filtering Tables with input
document.addEventListener("DOMContentLoaded", function() {
  let filterInput = document.getElementById('filter');
  let tableBody = document.getElementById("table-body");

  if (tableBody !== null) {
    let rows = tableBody.getElementsByTagName('tr');
    filterInput.addEventListener('keyup', () => {
      const filterValue = filterInput.value.toLowerCase();
      
      for (let i = 0; i < rows.length; i++) {
          const name = rows[i].getElementsByTagName('td')[1].textContent.toLowerCase();
          let found = false;
          const cells = rows[i].getElementsByTagName('td');

          for (let j = 0; j < cells.length; j++) {
              const cellText = cells[j].textContent.toLowerCase();
              if (cellText.includes(filterValue)) {
                  found = true;
                  break;
              }
          }
          if (found) {
              rows[i].style.display = '';
          } else {
              rows[i].style.display = 'none';
          }
      }
  });
  }
});