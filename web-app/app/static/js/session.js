// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebarToggle');

  // Function to apply the sidebar state
  function setSidebarState(isCollapsed) {
    if (isCollapsed) {
      sidebar.classList.add('collapsed');
    } else {
      sidebar.classList.remove('collapsed');
    }
  }

  // Load the saved state from local storage (default to false if not set)
  const isCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
  setSidebarState(isCollapsed);

  // Add toggle functionality
  sidebarToggle.addEventListener('click', function () {
    const isCollapsedNow = !sidebar.classList.contains('collapsed');
    setSidebarState(isCollapsedNow);
    localStorage.setItem('sidebarCollapsed', isCollapsedNow);
  });
});
