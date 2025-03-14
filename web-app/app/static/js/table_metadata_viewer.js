document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", function (event) {
      openTab(event, this.getAttribute("onclick").split("'")[1]);
    });
  });
  document.getElementById("schema").classList.remove("hidden");
});

function openTab(evt, tabName) {
  document
    .querySelectorAll(".tab-content")
    .forEach((tab) => tab.classList.add("hidden"));
  document
    .querySelectorAll(".tab-btn")
    .forEach((btn) =>
      btn.classList.remove("border-b-2", "border-blue-500", "text-blue-500"),
    );

  document.getElementById(tabName).classList.remove("hidden");
  evt.currentTarget.classList.add(
    "border-b-2",
    "border-blue-500",
    "text-blue-500",
  );
}
