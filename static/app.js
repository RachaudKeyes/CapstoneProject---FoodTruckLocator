// Range Slider

const range = document.querySelector("#rating");
const rangeValue = document.querySelector(".range-value");

rangeValue.textContent = range.value;

range.addEventListener("input", (e) => {
    rangeValue.textContent = e.target.value;
});