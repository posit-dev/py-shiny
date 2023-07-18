function mediapipeHand({callback, videoElement, canvasElement, options = {}, debug = false} = {}) {

  // Code taken from https://google.github.io/mediapipe/solutions/hands.html
  // and modified to set the Shiny input value when a hand is detected.

  const canvasCtx = canvasElement.getContext('2d');

  function onResults(results) {
    // Set Shiny input value
    if (results.multiHandLandmarks.length > 0) {
      callback(results);
    } else {
      callback(null);
    }

    // Do not draw anything unless debugging
    if (!debug) return;

    // Draw hand on canvas
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
    canvasCtx.drawImage(
        results.image, 0, 0, canvasElement.width, canvasElement.height);
    if (results.multiHandLandmarks) {
      for (const landmarks of results.multiHandLandmarks) {
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
                      {color: '#00FF00', lineWidth: 2});
        drawLandmarks(canvasCtx, landmarks, {color: '#FFFFFF', radius: 1});
      }
    }
    canvasCtx.restore();
  }
  const hands = new Hands({locateFile: (file) => {
    // TODO: This is totally cheating; this path is supposed to be an
    // implementation detail
    return `lib/@mediapipe/hands-1.0.0/${file}`;
  }});
  hands.setOptions(options);
  hands.onResults(onResults);

  const camera = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({image: videoElement});
    },
    width: 640,
    height: 480
  });
  camera.start();

}



class HandInputBinding extends Shiny.InputBinding {
  find(scope) {
    return $(scope).find("template.mediapipe-hand-input");
  }

  initialize(el) {
  }

  getValue(el) {
    return el.mediapipe_result || null;
  }

  setValue(el, value) {
    console.warn("setValue called on HandInputBinding, this is not implemented");
  }

  getRatePolicy(el) {
    return {
      policy: "throttle",
      delay: el.dataset.throttleDelay ?? 100
    };
  }

  subscribe(el, callback) {
    const id = this.getId(el);
    const options = JSON.parse(el.content.querySelector("script").innerText);
    const debug = el.matches(".mediapipe-hand-input-debug");
    const precision = el.dataset.precision || 3;

    const videoEl = document.createElement("video");
    videoEl.style.display = "none";
    const canvasEl = document.createElement("canvas");
    canvasEl.style.display = debug ? "block" : "none";
    canvasEl.style.position = "fixed";
    canvasEl.style.right = "12px";
    canvasEl.style.bottom = "12px";
    canvasEl.style.width = "320px";
    canvasEl.style.height = "240px";
    canvasEl.style.opacity = 0.85;

    document.body.appendChild(videoEl);
    document.body.appendChild(canvasEl);

    mediapipeHand({callback: (value) => {
      // We should allow the options to indicate what values are desired by the server.

      if (value) {
        // Quick and dirty rounding to 4 decimals
        value = JSON.parse(JSON.stringify(value, function(key, value) {
          if (key === "image") {
            return undefined;
          }

          if (typeof(value) === "number") {
            return +value.toFixed(precision);
          } else {
            return value;
          }
        }));
      }

      el.mediapipe_result = value;
      callback(true);
    }, videoElement: videoEl, canvasElement: canvasEl, options, debug});
  }

  unsubscribe(el) {
    // TODO: Destroy everything
  }
}

// var handInputBinding = new Shiny.InputBinding();
// $.extend(handInputBinding, {
//   find: function(scope) {
//     return $(scope).find(".increment");
//   },
//   getValue: function(el) {
//     return parseInt($(el).text());
//   },
//   setValue: function(el, value) {
//     $(el).text(value);
//   },
//   subscribe: function(el, callback) {
//     $(el).on("change.incrementBinding", function(e) {
//       callback();
//     });
//   },
//   unsubscribe: function(el) {
//     $(el).off(".incrementBinding");
//   }
// });

Shiny.inputBindings.register(new HandInputBinding());
