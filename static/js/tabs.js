// fetch calls
const fetch_song_path = async (ref_id) => {
  const songUrl = '/fetch-tab-path?' + new URLSearchParams({
    "ref_id": ref_id
  });
  tabData = await fetch(songUrl)
    .then(async (response) => {
      const data = await response.json();
      return data
    });
    return tabData;
}

window.addEventListener("load", async () => {
  // load elements
  const wrapper = document.querySelector(".at-wrap");
  const main = wrapper.querySelector(".at-main");
  var overlayText = document.getElementsByClassName("at-overlay-content")[0];

  // Getting the song data and path
  const gpID = document.querySelector("body").dataset.songFile;
  var hasAccess = document.querySelector("body").dataset.access;
  var premiumTab = document.querySelector("body").dataset.premium;
  let path = await fetch_song_path(gpID);

  // initialize alphatab
  const settings = {
    file: hasAccess != "False" && premiumTab == "True" || premiumTab == "False" ? path["path"] : "/static/uploads/tab-files/Deep Purple/Smoke On The Water.gp4",
    player: {
      enablePlayer: true,
      soundFont: "https://cdn.jsdelivr.net/npm/@coderline/alphatab@latest/dist/soundfont/sonivox.sf2",
      scrollElement: wrapper.querySelector('.at-viewport')
    },
  };

  const api = new alphaTab.AlphaTabApi(main, settings);

  // overlay logic
  const overlay = wrapper.querySelector(".at-overlay");
  api.renderStarted.on(() => {
    overlay.style.display = "flex";
  });
  api.renderFinished.on(() => {
    if(hasAccess == "False" && premiumTab == "True"){
      overlay.style.display = "flex";
      overlayText.innerText = "Only premium accounts can access premium tabs.";
    }
    else{
      overlay.style.display = "none";
    }
  });

  // track selector
  function createTrackItem(track) {
    const trackItem = document
      .querySelector("#at-track-template")
      .content.cloneNode(true).firstElementChild;
    trackItem.querySelector(".at-track-name").innerText = track.name;
    trackItem.track = track;
    trackItem.onclick = (e) => {
      e.stopPropagation();
      api.renderTracks([track]);
    };
    return trackItem;
  }
  const trackList = wrapper.querySelector(".at-track-list");
  api.scoreLoaded.on((score) => {
    // clear items
    trackList.innerHTML = "";
    // generate a track item for all tracks of the score
    score.tracks.forEach((track) => {
      trackList.appendChild(createTrackItem(track));
    });
  });
  api.renderStarted.on(() => {
    // collect tracks being rendered
    const tracks = new Map();
    api.tracks.forEach((t) => {
      tracks.set(t.index, t);
    });
    // mark the item as active or not
    const trackItems = trackList.querySelectorAll(".at-track");
    trackItems.forEach((trackItem) => {
      if (tracks.has(trackItem.track.index)) {
        trackItem.classList.add("active");
      } else {
        trackItem.classList.remove("active");
      }
    });
  });

  /** Controls **/
  api.scoreLoaded.on((score) => {
    wrapper.querySelector(".at-song-title").innerText = score.title;
    wrapper.querySelector(".at-song-artist").innerText = score.artist;
  });

  const countIn = wrapper.querySelector('.at-controls .at-count-in');
  countIn.onclick = () => {
    countIn.classList.toggle('active');
    if (countIn.classList.contains('active')) {
      api.countInVolume = 1;
    } else {
      api.countInVolume = 0;
    }
  };

  const metronome = wrapper.querySelector(".at-controls .at-metronome");
  metronome.onclick = () => {
    metronome.classList.toggle("active");
    if (metronome.classList.contains("active")) {
      api.metronomeVolume = 1;
    } else {
      api.metronomeVolume = 0;
    }
  };

  const loop = wrapper.querySelector(".at-controls .at-loop");
  loop.onclick = () => {
    loop.classList.toggle("active");
    api.isLooping = loop.classList.contains("active");
  };

  wrapper.querySelector(".at-controls .at-print").onclick = () => {
    api.print();
  };

  const zoom = wrapper.querySelector(".at-controls .at-zoom select");
  zoom.onchange = () => {
    const zoomLevel = parseInt(zoom.value) / 100;
    api.settings.display.scale = zoomLevel;
    api.updateSettings();
    api.render();
  };

  const layout = wrapper.querySelector(".at-controls .at-layout select");
  layout.onchange = () => {
    switch (layout.value) {
      case "horizontal":
        api.settings.display.layoutMode = alphaTab.LayoutMode.Horizontal;
        break;
      case "page":
        api.settings.display.layoutMode = alphaTab.LayoutMode.Page;
        break;
    }
    api.updateSettings();
    api.render();
  };

  // player loading indicator
  const playerIndicator = wrapper.querySelector(
    ".at-controls .at-player-progress"
  );
  api.soundFontLoad.on((e) => {
    const percentage = Math.floor((e.loaded / e.total) * 100);
    playerIndicator.innerText = percentage + "%";
  });
  api.playerReady.on(() => {
    playerIndicator.style.display = "none";
  });

  // main player controls
  const playPause = wrapper.querySelector(
    ".at-controls .at-player-play-pause"
  );
  const stop = wrapper.querySelector(".at-controls .at-player-stop");
  playPause.onclick = (e) => {
    if (e.target.classList.contains("disabled")) {
      return;
    }
    api.playPause();
  };
  stop.onclick = (e) => {
    if (e.target.classList.contains("disabled")) {
      return;
    }
    api.stop();
  };
  api.playerReady.on(() => {
    playPause.classList.remove("disabled");
    stop.classList.remove("disabled");
  });
  api.playerStateChanged.on((e) => {
    const icon = playPause.querySelector("i.fas");
    if (e.state === alphaTab.synth.PlayerState.Playing) {
      icon.classList.remove("fa-play");
      icon.classList.add("fa-pause");
    } else {
      icon.classList.remove("fa-pause");
      icon.classList.add("fa-play");
    }
  });

  // song position
  function formatDuration(milliseconds) {
    let seconds = milliseconds / 1000;
    const minutes = (seconds / 60) | 0;
    seconds = (seconds - minutes * 60) | 0;
    return (
      String(minutes).padStart(2, "0") +
      ":" +
      String(seconds).padStart(2, "0")
    );
  }

  const songPosition = wrapper.querySelector(".at-song-position");
  let previousTime = -1;
  api.playerPositionChanged.on((e) => {
    // reduce number of UI updates to second changes.
    const currentSeconds = (e.currentTime / 1000) | 0;
    if (currentSeconds == previousTime) {
      return;
    }

    songPosition.innerText =
      formatDuration(e.currentTime) + " / " + formatDuration(e.endTime);
  });

  // Nav menu responsiveness
  var mobileHeader = document.getElementById("mobile-header");
  var nonMobileHeader = document.getElementById("page-top");

  if(window.innerWidth < 700){
      nonMobileHeader.style.display = "none";
      mobileHeader.style.display = "flex";
  }
  else{
      nonMobileHeader.style.display = "flex"
      mobileHeader.style.display = "none";
  }

  this.window.addEventListener("resize", function(){
      if(this.innerWidth < 700){
          nonMobileHeader.style.display = "none";
          mobileHeader.style.display = "flex";
      }
      else{
          nonMobileHeader.style.display = "flex"
          mobileHeader.style.display = "none";
      }
  });

  // Menu button login
  var menuBtn = document.getElementsByClassName("nav-menu-btn")[0];
  var content = document.getElementsByClassName("links-content")[0];

  menuBtn.addEventListener("click", function(){
      if(!menuBtn.className.includes("active")){
          menuBtn.classList.add("active");
          content.style.maxHeight = content.scrollHeight + "px";
      }
      else{
          menuBtn.classList.remove("active");
          content.style.maxHeight = null;
      }
  });
});