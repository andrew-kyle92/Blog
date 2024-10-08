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
  var settings = new alphaTab.Settings();
  settings.core.file = hasAccess != "False" && premiumTab == "True" || premiumTab == "False" ? path["path"] : "/static/uploads/tab-files/Deep Purple/Smoke On The Water.gp4";
  //settings.core.tracks = "all";
  settings.player.enablePlayer = true;
  settings.player.soundFont = "https://cdn.jsdelivr.net/npm/@coderline/alphatab@latest/dist/soundfont/sonivox.sf2";
  settings.player.scrollElement = wrapper.querySelector('.at-viewport');
  
  const api = new alphaTab.AlphaTabApi(main, settings);

  // overlay logic
  const overlay = wrapper.querySelector(".at-overlay");
  api.renderStarted.on(() => {
    overlay.style.display = "flex";
  });
  api.renderFinished.on(() => {
    if(hasAccess === "False" && premiumTab === "True"){
      overlay.style.display = "flex";
      overlayText.innerText = "Only premium accounts can access premium tabs.";
    }
    else{
      overlay.style.display = "none";
    }
  });
  
  var trackIcons = {
	  drums: 'fa-drum',
	  guitar: 'fa-guitar',
  }

  // track selector
  function createTrackItem(track) {
    // getting the icon
    let iconClass = track.name.toLowerCase().includes('drums') ? trackIcons.drums
					: track.name.toLowerCase().includes('drumkit') ? trackIcons.drums
					: trackIcons.guitar;
    // setting the track template
    const trackItem = document.getElementById("at-track-template").content.firstElementChild.cloneNode(true);
    // setting the track name
    trackItem.querySelector(".at-track-name").innerText = track.name;
    // setting the track icon
	trackItem.querySelector(".fas").classList.add(iconClass);
    // setting the track volume
    let vol = ((track.playbackInfo.volume / 16) * 2) * 8
    trackItem.querySelector(".track-vol").value = vol;
    trackItem.querySelector('.track-vol').setAttribute('value', vol)
    trackItem.track = track;
    // track functions
    trackItem.onclick = (e) => {
      e.stopPropagation();
      if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
        api.renderTracks([track]);
      }
    };

    // button and volume logic
    let trackMuteBtn = trackItem.querySelector('.muteBtn');
    trackMuteBtn.onclick = () =>{
      if (!track.playbackInfo.isMute) {
        // setting the sound to mute
        api.changeTrackMute([track], true);
        // setting the track isMute
        track.playbackInfo.isMute = true;
        // changing the btn color
        trackMuteBtn.classList.add('active');
      }
      else {
        // unmuting the sound
        api.changeTrackMute([track], false);
        // setting the isMute: false
        track.playbackInfo.isMute = false;
        // changing the btn color
        trackMuteBtn.classList.remove('active');
      }
    }

    let trackSoloBtn = trackItem.querySelector('.soloBtn');
    trackSoloBtn.onclick = () =>{
      if (!track.playbackInfo.isSolo) {
        // setting the sound to mute
        api.changeTrackSolo([track], true);
        // setting the track isMute
        track.playbackInfo.isSolo = true;
        // changing the btn color
        trackSoloBtn.classList.add('active');
      }
      else {
        // unmuting the sound
        api.changeTrackSolo([track], false);
        // setting the isMute: false
        track.playbackInfo.isSolo = false;
        // changing the btn color
        trackSoloBtn.classList.remove('active');
      }
    }

    let volumeSlider = trackItem.querySelector('.track-vol');
    volumeSlider.onchange = () => {
      let maxSliderVal = 16;
      let sliderVol = volumeSlider.value;
      let adjustedVolume = ((sliderVol / maxSliderVal) * 2);
      api.changeTrackVolume([track], adjustedVolume);
    }

    return trackItem;
  }
 
	const trackList = wrapper.querySelector(".at-track-list");
	// fill track list when the score is loaded
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