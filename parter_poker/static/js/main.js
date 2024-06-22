const slider = document.querySelector("#vibrator_input");
const onlineUsersValue = document.querySelector("#online-users-value");
const sliderValue = document.getElementById("the-value");
const evtSource = new EventSource("listen");

var timerId;

evtSource.addEventListener("newIntensity", (event) => {
    const new_intensity = JSON.parse(event.data);
    console.log(`Received intensity of ${new_intensity.intensity}!`)
    sliderValue.innerHTML = new_intensity.intensity;
    slider.value = new_intensity.intensity;
});

evtSource.addEventListener("newListener", (event) => {
    const new_intensity = JSON.parse(event.data);
    console.log(`Received new user count of ${new_intensity.listeners}!`)
    onlineUsersValue.innerHTML = new_intensity.listeners;
});

// Update the current slider value (each time you drag the slider handle)
slider.addEventListener("input", (event) => {
    // If setTimeout is already scheduled, no need to do anything
	if (timerId) {
		return
	}

	timerId = setTimeout(function() {
	    fetch("/toy/intensity", {
            method: "POST",
            body: JSON.stringify({
                intensity: event.target.value
            }),
            headers: {
                "Content-type": "application/json; charset=UTF-8"
            }
        });
        console.log(`Set intensity to ${event.target.value}!`);
        sliderValue.innerHTML = event.target.value;
        timerId = undefined;
	}, 200);
});

//slider.oninput = function() {
//    fetch("/toy/intensity", {
//        method: "POST",
//        body: JSON.stringify({
//            intensity: this.value
//        }),
//        headers: {
//            "Content-type": "application/json; charset=UTF-8"
//        }
//    });
//    sliderValue.innerHTML = this.value;
//}

const htmlTag = document.querySelector("html");
const switchTheme = document.querySelector(".switch-theme");
switchTheme.onclick = function () {
  if (htmlTag.getAttribute("data-theme") === "dark") {
    htmlTag.setAttribute("data-theme", "");
  } else {
    htmlTag.setAttribute("data-theme", "dark");
  }
};