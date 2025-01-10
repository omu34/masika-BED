document.addEventListener("DOMContentLoaded", async function () {
    // Params
    const animationDuration = 3000;
    const autoplayDelay = 4000;

    // UI
    const sectionWrapper = document.querySelector("#slider-wrapper");

    // Image Slider
    const imageSlider = new KeenSlider(
        "#image-slider",
        {
            loop: true,
            defaultAnimation: {
                duration: animationDuration,
            },
            detailsChanged: (s) => {
                s.slides.forEach((element, idx) => {
                    element.style.opacity = s.track.details.slides[idx].portion;
                });
            },
            renderMode: "custom",
        },
        [
            (slider) => {
                let timeout;
                let mouseOver = false;
                function clearNextTimeout() {
                    clearTimeout(timeout);
                }
                function nextTimeout() {
                    clearTimeout(timeout);
                    if (mouseOver) return;
                    timeout = setTimeout(() => {
                        slider.next();
                    }, autoplayDelay);
                }
                slider.on("created", () => {
                    slider.container.addEventListener("mouseover", () => {
                        mouseOver = true;
                        clearNextTimeout();
                    });
                    slider.container.addEventListener("mouseout", () => {
                        mouseOver = false;
                        nextTimeout();
                    });
                    nextTimeout();
                });
                slider.on("dragStarted", clearNextTimeout);
                slider.on("animationEnded", nextTimeout);
                slider.on("updated", nextTimeout);
            },
        ]
    );

    // Text Slider
    const textSlider = new KeenSlider(
        "#text-slider",
        {
            defaultAnimation: {
                duration: animationDuration,
            },
            loop: true,
            slides: {
                origin: "center",
                perView: 2,
                spacing: 15,
            },
            detailsChanged: (s) => {
                const slides = s.track.details.slides;
                s.slides.forEach((element, idx) => {
                    scaleElement(element.querySelector("div"), slides[idx].portion);
                });
            },
            initial: 0,
        },
        [SyncSlidersPlugin(imageSlider)]
    );

    function scaleElement(element, portion) {
        const scale_size = 0.75;
        const scale = 1 - (scale_size - scale_size * portion);
        const scale_style = `scale(${scale})`;
        element.style.transform = scale_style;
        element.style["-webkit-transform"] = scale_style;

        const opacity = portion === 1 ? 1 : 0.2;
        element.style.opacity = String(opacity);
    }

    // Sync sliders
    function SyncSlidersPlugin(secondSlider) {
        return (firstSlider) => {
            firstSlider.on("created", () => {
                // Sync
                secondSlider.on("slideChanged", (secondSlider) => {
                    const nextId = secondSlider.track.details.rel;

                    firstSlider.moveToIdx(nextId);
                });

                firstSlider.on("slideChanged", (firstSlider) => {
                    const nextId = firstSlider.track.details.rel;

                    secondSlider.moveToIdx(nextId);
                });

                // Click on Wrapper
                sectionWrapper.addEventListener("click", () => {
                    firstSlider.next();
                });
            });
        };
    }
});