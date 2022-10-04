// ################## All the DB fetch calls for the music.js script ##################
const fetch_artists = async () => {
    const artistUrl = 'fetch-artists';
    let artistData = await fetch(artistUrl)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return artistData;
}

const fetch_albums = async (artist_id) => {
    const albumUrl = 'fetch-albums?' + new URLSearchParams({
        "artist_id": artist_id
    });
    let albumData = await fetch(albumUrl)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return albumData;
}

const fetch_album_songs = async (album_id) => {
    const songs_url = "fetch-album-songs?" + new URLSearchParams({
        "album_id": album_id
    });
    let songData = await fetch(songs_url)
        .then(async response => {
            const data = response.json();
            return data
        });
    return songData;
}

const fetch_songs = async (shuffled) => {
    const songs_url = 'fetch-songs?' + new URLSearchParams({
        "shuffled": shuffled
    });
    let songData = await fetch(songs_url)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return songData;
}

const fetch_song = async (_id) => {
    const song_url = "fetch-song?" + new URLSearchParams({
        "_id": _id
    });
    let songData = await fetch(song_url)
        .then(async (response) => {
            const data = await response.json();
            return data;
        });
    return songData;
}

const fetch_previous_next_tracks = async (refId) => {
    tracksUrl = "fetch-previous-next-tracks?" + new URLSearchParams({
        "refId": refId
    });
    let tracksData = await fetch(tracksUrl)
        .then(async (response) => {
            const data = response.json();
            return data
        });
    return tracksData;
}

// ################## Music Player UI Button Variables ##################
const playPauseBtn = document.getElementById("play-pause-btn");
const backBtn = document.getElementById("back-btn");
const forwardBtn = document.getElementById("forward-btn");
const volumeUpBtn = document.getElementsByClassName("fa-volume-up");
const volumeDownBtn = document.getElementsByClassName("fa-volume-off");
const shuffleBtn = document.getElementById("shuffle-btn");
const loopBtn = document.getElementById("loop-btn");
// ################## Script Variables ##################
var sideBarOuterListContent = document.getElementById("outer-level-content");
var songInfo = document.getElementsByClassName("track-info song")[0];
var artistInfo = document.getElementsByClassName("track-info artist")[0];
var albumInfo = document.getElementsByClassName("track-info album")[0];
var progressBar = document.getElementsByClassName("seek_slider")[0];
var volumeBar = document.getElementsByClassName("volume_slider")[0];
var songItem = document.getElementsByClassName("song-item");
var songs = document.getElementsByClassName("lower-level-tab");
var songImg = document.getElementsByClassName("song-img")[0];
var currentTrack = null;
var songPlaying = false;
var loopOn = false;
var loopPlaylist = [];
var shuffleOn = false;
var backBtnClicked = false;
var forwardBtnClicked = false;
var manualSongSelected = false;


// ################## Main functions ##################

const getArtists = async () => {
    let artists = await fetch_artists();
    var queryString = document.location.search;
    var urlParams = new URLSearchParams(queryString);
    let song;
    if(urlParams.get("track_id")){
        song = await fetch_song(urlParams.get("track_id"))
        currentTrack = setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
    }
    for(var i = 0; i < Object.keys(artists).length; i++){
        let artistName = artists[Object.keys(artists)[i]];
        let artistId = Object.keys(artists)[i];
        // Div element Creation and assignment
        let div = document.createElement("div");
        div.setAttribute("id", "artist-" + artistId);
        div.setAttribute("class", "middle-level-content");
        div.title = artistName;
        div.setAttribute("onclick", `albumDropDown(${artistId})`);
        sideBarOuterListContent.appendChild(div);
        // span Element creation and design
        let parentDiv = document.getElementById("artist-" + artistId);
        let span = document.createElement("span");
        span.setAttribute("class", "music-content-artist");
        span.innerHTML = `<i class="fa-solid fa-caret-right"></i> ${artistName}`;
        parentDiv.appendChild(span);
    }
}

const albumDropDown = async (id) => {
    let div = document.getElementById("artist-" + id);
    let artist = div.title;
    if(!div.className.includes("expanded")){
        div.setAttribute("class", "middle-level-content expanded");
        div.firstChild.innerHTML = `<i class="fa-solid fa-caret-down"></i> ${artist}`;
        // Fetching artist albums
        let albums = await fetch_albums(id);
        // creating inner level div
        let newDiv = document.createElement("div");
        newDiv.setAttribute("id", `content-${artist}-albums`);
        newDiv.setAttribute("class", "inner-level-content");
        div.parentElement.insertBefore(newDiv, div.nextSibling);
        for(let i = 0; i < Object.keys(albums).length; i++){
            // creating album span element
            let divElement = document.getElementById(`content-${artist}-albums`);
            let span = document.createElement("span");
            let albumName = albums[i]["album"];
            let albumId = albums[i]["id"];
            span.setAttribute("id", albumId);
            if(currentTrack){
                if(albumInfo.innerText == albumName){
                    span.setAttribute("class", "music-content-albums span-active");
                }
                else{
                    span.setAttribute("class", "music-content-albums");
                }
            }
            else{
                span.setAttribute("class", "music-content-albums");
            }
            span.title = albumName;
            span.setAttribute("onclick", `getAlbumSongs('${albumName}', ${albumId})`);
            span.innerHTML = albumName;
            divElement.appendChild(span);
        }
    }
    else{
        // destroying the album content for less memory usage
        let albumDiv = document.getElementById(`content-${artist}-albums`);
        div.firstChild.innerHTML = `<i class="fa-solid fa-caret-right"></i> ${artist}`;
        div.setAttribute("class", "middle-level-content");
        albumDiv.remove();
    }
}

const getAlbumSongs = async (albumName, id) => {
    if(!document.getElementById("side-bar-songs-content")){
        let albumDiv = document.getElementById(id);
        albumDiv.setAttribute("class", "music-content-albums span-active");
        let outerDiv = document.getElementById("side-bar-mid");
        // Creating sibling div to className mid-content
        let newDiv = document.createElement("div");
        newDiv.setAttribute("id", "side-bar-songs-content");
        newDiv.setAttribute("class", "mid-content");
        outerDiv.appendChild(newDiv);
        // creating the title div
        let songsDiv = document.getElementById("side-bar-songs-content");
        let titleDiv = document.createElement("div");
        titleDiv.setAttribute("id", "title-div");
        songsDiv.appendChild(titleDiv);
        // creating the title span
        let spanParentDiv = document.getElementById("title-div");
        let titleSpan = document.createElement("span");
        titleSpan.setAttribute("class", "music-content-title");
        titleSpan.innerText = "Songs";
        spanParentDiv.appendChild(titleSpan);
        // creating the album title span
        let albumTitleDiv = document.createElement("span");
        albumTitleDiv.setAttribute("id", "album-title")
        albumTitleDiv.setAttribute("class", "music-content-title");
        albumTitleDiv.innerText = albumName
        spanParentDiv.appendChild(albumTitleDiv);
        // creating songs div
        let innerDiv = document.createElement("div");
        innerDiv.setAttribute("id", "songs-outer-content");
        innerDiv.setAttribute("class", "inner-level-content");
        songsDiv.appendChild(innerDiv);
        // fetching songs corresponding to the album id
        let albumSongs = await fetch_album_songs(id);
        // creating a span element for every song in the album
        let songParentDiv = document.getElementById("songs-outer-content");
        for(let i = 0; i < Object.keys(albumSongs).length; i++){
            let songSpan = document.createElement("span");
            songSpan.setAttribute("id", Object.keys(albumSongs)[i]);
            if(currentTrack){
                if(albumSongs[Object.keys(albumSongs)[i]["song_name"] == songInfo.innerText]){
                    songSpan.setAttribute("class", "song-item song-playing");
                }
                else{
                    songSpan.setAttribute("class", "song-item");
                }
            }
            else{
                songSpan.setAttribute("class", "song-item");
            }
            songSpan.setAttribute("onclick", `playTrack('${Object.keys(albumSongs)[i]}')`)
            songSpan.title = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
            songSpan.innerText = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
            songParentDiv.appendChild(songSpan);
        }
    }
    else{
        if(document.getElementsByClassName("span-active").length == 0){
            // adding the active-class to selected album
            let selectedAlbum = document.getElementById(id);
            selectedAlbum.setAttribute("class", "music-content-albums span-active");
            // fetching songs corresponding to the album id
            let albumSongs = await fetch_album_songs(id);
            // adding the album name to the albumTitleSpan
            let albumTitleSpan = document.getElementById("album-title");
            albumTitleSpan.innerText = albumName;
            // creating a span element for every song in the album
            let songParentDiv = document.getElementById("songs-outer-content");
            // removing current list of songs
            while(songParentDiv.firstChild){
                songParentDiv.removeChild(songParentDiv.lastChild);
            }
            // adding new list of songs
            for(let i = 0; i < Object.keys(albumSongs).length; i++){
                let songSpan = document.createElement("span");
                songSpan.setAttribute("id", Object.keys(albumSongs)[i]);
                songSpan.setAttribute("class", "song-item");
                songSpan.setAttribute("onclick", `playTrack('${Object.keys(albumSongs)[i]}')`)
                songSpan.title = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
                songSpan.innerText = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
                songParentDiv.appendChild(songSpan);
            }
        }
        else{
            let currentAlbumSelected = document.getElementsByClassName("span-active")[0];
            let currentTrackId = currentAlbumSelected.id
            currentAlbumSelected.setAttribute("class", "music-content-albums");
            let songParentDiv = document.getElementById("songs-outer-content");
            while(songParentDiv.firstChild){
                songParentDiv.removeChild(songParentDiv.lastChild);
            }
            if(currentTrackId != id){
                // adding the active-class to selected album
                let selectedAlbum = document.getElementById(id);
                selectedAlbum.setAttribute("class", "music-content-albums span-active");
                // adding the album name to the albumTitleSpan
                let albumTitleSpan = document.getElementById("album-title");
                albumTitleSpan.innerText = albumName;
                // fetching songs corresponding to the album id
                let albumSongs = await fetch_album_songs(id);
                // creating a span element for every song in the album
                let songParentDiv = document.getElementById("songs-outer-content");
                for(let i = 0; i < Object.keys(albumSongs).length; i++){
                    let songSpan = document.createElement("span");
                    songSpan.setAttribute("id", Object.keys(albumSongs)[i]);
                    songSpan.setAttribute("class", "song-item");
                    songSpan.setAttribute("onclick", `playTrack('${Object.keys(albumSongs)[i]}')`)
                    songSpan.title = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
                    songSpan.innerText = albumSongs[Object.keys(albumSongs)[i]]["song_name"];
                    songParentDiv.appendChild(songSpan);
                }
            }
        }
    }
}

function setTrack(song, id) {
    songImg.setAttribute("src", song["album_art"]);
    duration = document.getElementsByClassName("seconds-start")[0];
    songInfo.innerText = song["song_name"];
    artistInfo.innerText = song["artist"];
    albumInfo.innerText = song["album"];
    if(currentTrack == null){
        currentTrack = new Audio(song["song_file"]);
        currentTrack.id = id;
    }
    else{
        currentTrack.src = song["song_file"];
        currentTrack.id = id;
    }
    setTrackUrl(id);
    songPlaying = true;
    sec = parseInt(currentTrack.currentTime % 60);
    min = parseInt((currentTrack.currentTime / 60) % 60);
    if(sec < 10){
        duration.innerText = min + ":0" + sec;
    }
    else{
        duration.innerText = min + ":" + sec;
    }
    endDuration = document.getElementsByClassName("seconds-end")[0];
    songDurationM = parseInt((currentTrack.duration / 60) % 60);
    songDurationS = parseInt(currentTrack.duration % 60)
    if(songDurationS < 10){
        endDuration.innerText = songDurationM + ":0" + songDurationS;
    }
    else{
        endDuration.innerText = songDurationM + ":" + songDurationS;
    }

    updateTime();

    let selectedSong = document.getElementById(id);
    if(selectedSong){
        selectedSong.setAttribute("class", "song-item song-playing");
    }

    return currentTrack
}

function setTrackUrl(songId){
    const state = { "widget": "False", "track_id": songId };
    const url = "music-player?widget=False&track_id=" + songId;
    window.history.pushState(state, "", url);
}

function seekTo(){
    seek_to = currentTrack.duration * (progressBar.value / 100);
    currentTrack.currentTime = seek_to;
}

function setVolume() {
  // Set the volume according to the
  // percentage of the volume slider set
  currentTrack.volume = volumeBar.value / 100;
}

function updateTime(){
    currentTrack.addEventListener("timeupdate", function(){
        if(currentTrack.ended){
            if(loopOn){
                if(!backBtnClicked || !manualSongSelected){
                    currentTrack.pause();
                    currentTrack.currentTime = 0;
                    playNextTrack();
                }
                else{
                    backBtnClicked = false;
                    manualSongSelected = false;
                }
            }
            else{
                currentTrack.currentTime = 0;
                songPlaying = false;
                playPauseBtn.setAttribute("class", "fa-solid fa-circle-play");
            }
        }
        else{
            duration = document.getElementsByClassName("seconds-start")[0];
            s = parseInt(currentTrack.currentTime % 60);
            m = parseInt((currentTrack.currentTime / 60) % 60);
            if(s < 10){
                duration.innerText = m + ":0" + s;
            }
            else{
                duration.innerText = m + ":" + s;
            }
        }
    });
    // End time update
    currentTrack.addEventListener("timeupdate", function(){
        endDuration = document.getElementsByClassName("seconds-end")[0];
        songDurationM = parseInt((currentTrack.duration / 60) % 60);
        songDurationS = parseInt(currentTrack.duration % 60)
        if(songDurationS < 10){
            endDuration.innerText = songDurationM + ":0" + songDurationS;
        }
        else{
            endDuration.innerText = songDurationM + ":" + songDurationS;
        }
    });
    // Progress Bar update
    currentTrack.addEventListener("timeupdate", function(){
        if(currentTrack.ended){
            sliderProgress = 0;
        }
        else{
            sliderValue = parseInt(progressBar.value);
            sliderProgress = progressBar.value = currentTrack.currentTime * (100 / currentTrack.duration);
        }
    });
};

var playTrack = async (refId) =>{
    manualSongSelected = true;
    if(currentTrack != null){
        let currentSong = document.getElementsByClassName("song-playing")[0];
        if(currentSong){
            currentSong.setAttribute("class", "song-item");
        }
        currentTrack.currentTime = 0;
        songPlaying = false;
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-play");
    }
    let song = await fetch_song(refId);
    currentTrack = setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
    currentTrack.play();
    playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
};

async function playNextTrack(){
    let nextTrack = null;
    for(let i = 0; i < loopPlaylist.length; i++){
        if(currentTrack.id == Object.keys(loopPlaylist[i])[0]){
            nextTrack = i + 1;
            break;
        }
    }
    let currentSong = document.getElementById(currentTrack.id);
    currentSong.setAttribute("class", "song-item");
    if(nextTrack == loopPlaylist.length){
        let refId = Object.keys(loopPlaylist[0])[0]
        let song = await fetch_song(refId);
        currentTrack = setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
    }
    else{
        let refId = Object.keys(loopPlaylist[nextTrack])[0]
        let song = await fetch_song(refId);
        currentTrack = setTrack(song[refId], refId);
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
    }

}

// ################## Button Logic ##################
playPauseBtn.addEventListener("click", function(){
    if(currentTrack != null){
        if(playPauseBtn.className == "fa-solid fa-circle-play"){
            songPlaying = true;
            playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
            currentTrack.play();
        }
        else{
            playPauseBtn.setAttribute("class", "fa-solid fa-circle-play");
            songPlaying = false;
            currentTrack.pause();
        }
    }
    else{
        // creating no song selected flag
        let parentDiv = document.getElementById("main-content");
        let newSpan = document.createElement("span");
        newSpan.id = "no-song-flag";
        newSpan.innerText = "No song selected";
        parentDiv.insertBefore(newSpan, parentDiv.firstElementChild);
        // destroying the span after 5 seconds
        setTimeout(() => {
            parentDiv.removeChild(parentDiv.firstElementChild);
        }, 7500);
    }
});

backBtn.addEventListener("click", async function(){
    if(currentTrack != null){
        let trackInfo = await fetch_previous_next_tracks(currentTrack.id);
        backBtnClicked = true;
        if(currentTrack.currentTime < 5){
            currentTrack.pause();
            currentTrack.currentTime = 0;
            songPlaying = false;
            playPauseBtn.setAttribute("class", "fa-solid fa-circle-play");
            let songSelected = document.getElementsByClassName("song-playing")[0];
            if(songSelected){
                songSelected.setAttribute("class", "song-item");
            }
            let song;
            if(loopOn){
                let previousTrack;
                for(let i = 0; i < loopPlaylist.length; i++){
                    if(Object.keys(loopPlaylist[i])[0] == currentTrack.id){
                        if(i == 0){
                            previousTrack = loopPlaylist.length - 1;
                        }
                        else{
                            previousTrack = i - 1;
                        }
                    }

                }
                song = await fetch_song(Object.keys(loopPlaylist[previousTrack])[0]);
            }
            else{
                song = await fetch_song(trackInfo["previous_track"]["ref_id"]);
            }
            if(!loopOn){
                let albumTitle = document.getElementById("album-title");
                if(albumTitle){
                    albumTitle.innerText = song[Object.keys(song)[0]]["album"]; 
                    let songsDiv = document.getElementById("songs-outer-content");
                    while(songsDiv.childElementCount > 0){
                        songsDiv.removeChild(songsDiv.firstElementChild);
                    }
                    // creating song span in songs list
                    let newSpan = document.createElement("span");
                    newSpan.setAttribute("id", `${Object.keys(song)[0]}`);
                    newSpan.setAttribute("class", "song-item");
                    newSpan.title = song[Object.keys(song)[0]]["song_name"];
                    newSpan.innerText = song[Object.keys(song)[0]]["song_name"];
                    newSpan.setAttribute("onclick", `playTrack('${Object.keys(song)[0]}')`);
                    songsDiv.appendChild(newSpan);
                }
            }
            currentTrack = setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
        }
        else{
            currentTrack.currentTime = 0;
        }
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
    }
    else{
        // creating no song selected flag
        let parentDiv = document.getElementById("main-content");
        let newSpan = document.createElement("span");
        newSpan.id = "no-song-flag";
        newSpan.innerText = "No song selected";
        parentDiv.insertBefore(newSpan, parentDiv.firstElementChild);
        // destroying the span after 5 seconds
        setTimeout(() => {
            parentDiv.removeChild(parentDiv.firstElementChild);
        }, 7500);
    }
});

forwardBtn.addEventListener("click", async function(){
    if(currentTrack != null){
        let song;
        forwardBtnClicked = true;
        currentTrack.pause();
        currentTrack.currentTime = 0;
        songPlaying = false;
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-play");
        if(!loopPlaylist.length == 0){
            let nextTrack;
            for(let i = 0; i < loopPlaylist.length; i++){
                if(Object.keys(loopPlaylist[i])[0] == currentTrack.id){
                    nextTrack = i == loopPlaylist.length - 1 ? 0
                                : i == 0 ? 1 : i + 1;
                    break;
                }
            }
            let songSelected = document.getElementsByClassName("song-playing")[0];
            if(songSelected){
                songSelected.setAttribute("class", "song-item");
            }
            song = await fetch_song(Object.keys(loopPlaylist[nextTrack])[0]);
        }
        else{
            let trackInfo = await fetch_previous_next_tracks(currentTrack.id);
            song = await fetch_song(trackInfo["next_track"]["ref_id"])
        }
        if(!loopOn){
            let albumTitle = document.getElementById("album-title");
            if(albumTitle){
                albumTitle.innerText = song[Object.keys(song)[0]]["album"];
                let songsDiv = document.getElementById("songs-outer-content");
                while(songsDiv.childElementCount > 0){
                    songsDiv.removeChild(songsDiv.firstElementChild);
                }
                // creating song span in songs list
                let newSpan = document.createElement("span");
                newSpan.setAttribute("id", `${Object.keys(song)[0]}`);
                newSpan.setAttribute("class", "song-item");
                newSpan.title = song[Object.keys(song)[0]]["song_name"];
                newSpan.innerText = song[Object.keys(song)[0]]["song_name"];
                newSpan.setAttribute("onclick", `playTrack('${Object.keys(song)[0]}')`);
                songsDiv.appendChild(newSpan);
            }
        }
        currentTrack = setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
        currentTrack.play();
        playPauseBtn.setAttribute("class", "fa-solid fa-circle-pause");
    }
    else{
        // creating no song selected flag
        let parentDiv = document.getElementById("main-content");
        let newSpan = document.createElement("span");
        newSpan.id = "no-song-flag";
        newSpan.innerText = "No song selected";
        parentDiv.insertBefore(newSpan, parentDiv.firstElementChild);
        // destroying the span after 5 seconds
        setTimeout(() => {
            parentDiv.removeChild(parentDiv.firstElementChild);
        }, 7500);
    }
});

loopBtn.addEventListener("click", async () => {
    if(loopBtn.dataset.active == "false"){
        loopBtn.style.color = "#8c8c8c";
        loopBtn.dataset.active = "true";
        loopOn = true;
        if(!shuffleOn){
            // removing the songs div
            let midSection = document.getElementById("side-bar-mid");
            for(let i = 0; i < midSection.childElementCount; i++){
                if(midSection.children[i].id == "side-bar-songs-content"){
                    midSection.removeChild(midSection.children[i]);
                    break;
                }
            }
            let playListDiv = document.getElementById("side-bar-bottom");
            playListDiv.style.background = "#4f4d4d";
            // creating the title span
            let titleSpan = document.createElement("span");
            titleSpan.setAttribute("id", "playlist-top");
            titleSpan.setAttribute("class", "playlist-title");
            titleSpan.innerText = "Playlist";
            playListDiv.appendChild(titleSpan);
            // getting all songs
            let loopList = await fetch_songs("false");
            for(let i = 0; i < loopList["songs"].length; i++){
                loopPlaylist.push(loopList["songs"][i]);
            }
            // creating a span for every playlist song
            for(let i = 0; i < loopPlaylist.length; i++){
                let songSpan = document.createElement("span");
                songSpan.setAttribute("id", Object.keys(loopPlaylist[i])[0]);
                if(currentTrack != null){
                    if(songSpan.id == currentTrack.id){
                        songSpan.setAttribute("class", "song-item song-playing");
                    }
                    else{
                        songSpan.setAttribute("class", "song-item");
                    }
                }
                else{
                    songSpan.setAttribute("class", "song-item");
                }
                songSpan.setAttribute("onclick", `playTrack('${Object.keys(loopPlaylist[i])[0]}')`);
                songSpan.innerText = loopPlaylist[i][Object.keys(loopPlaylist[i])[0]]["song_name"];
                playListDiv.appendChild(songSpan);
            }
        }
        if(document.getElementsByClassName("song-playing").length == 0){
            let song = await fetch_song(`${Object.keys(loopPlaylist[0])[0]}`);
            setTrack(song[Object.keys(song)[0]], Object.keys(song)[0]);
        }
    }
    else{
        let playlistDiv = document.getElementById("side-bar-bottom");
        while(playlistDiv.childElementCount > 0){
            playlistDiv.removeChild(playlistDiv.firstElementChild);
        }
        playlistDiv.style.background = "#2e2d2d";
        loopBtn.style.color = "black";
        loopBtn.dataset.active = "false";
        loopPlaylist = [];
        loopOn = false;
    }
});

loopBtn.addEventListener("mouseover", () => {
    loopBtn.style.color = "#b8b8b8";
});

loopBtn.addEventListener("mouseout", () => {
    if(loopBtn.dataset.active == "false"){
        loopBtn.style.color = "black";
    }
    else{
        loopBtn.style.color = "#8c8c8c";
    }
});

shuffleBtn.addEventListener("click", async () => {
    if(shuffleBtn.dataset.active == "false"){
        shuffleOn = true;
        shuffleBtn.style.color = "#8c8c8c";
        shuffleBtn.dataset.active = "true";
        let midSection = document.getElementById("side-bar-mid");
        for(let i = 0; i < midSection.childElementCount; i++){
            if(midSection.children[i].id == "side-bar-songs-content"){
                midSection.removeChild(midSection.children[i]);
                break;
            }
        }
        let playListDiv = document.getElementById("side-bar-bottom");
        if(loopOn){
            while(playListDiv.childElementCount > 0){
                playListDiv.removeChild(playListDiv.firstElementChild);
            }
            loopPlaylist = [];
        }
        playListDiv.style.background = "#4f4d4d";
        // creating the title span
        let titleSpan = document.createElement("span");
        titleSpan.setAttribute("id", "playlist-top");
        titleSpan.setAttribute("class", "playlist-title");
        titleSpan.innerText = "Shuffled Playlist";
        playListDiv.appendChild(titleSpan);
        let loopList = await fetch_songs("true");
        for(let i = 0; i < loopList["songs"].length; i++){
            loopPlaylist.push(loopList["songs"][i]);
        }
        // creating a span for every playlist song
        for(let i = 0; i < loopPlaylist.length; i++){
            let songSpan = document.createElement("span");
            songSpan.setAttribute("id", Object.keys(loopPlaylist[i])[0]);
            if(currentTrack != null){
                if(songSpan.id == currentTrack.id){
                    songSpan.setAttribute("class", "song-item song-playing");
                }
                else{
                    songSpan.setAttribute("class", "song-item");
                }
            }
            else{
                songSpan.setAttribute("class", "song-item");
            }
            songSpan.setAttribute("onclick", `playTrack('${Object.keys(loopPlaylist[i])[0]}')`);
            songSpan.innerText = loopPlaylist[i][Object.keys(loopPlaylist[i])[0]]["song_name"];
            playListDiv.appendChild(songSpan);
        }
        if(!loopOn){
            loopBtn.click();
            loopOn = true;
        }
        else{
            loopPlaylist = [];
        }
    }
    else{
        shuffleBtn.style.color = "black";
        shuffleBtn.dataset.active = "false";
        if(loopOn){
            loopBtn.click();
            loopOn = false;
        }
        shuffleOn = false;
        loopPlaylist = [];
    }
});

shuffleBtn.addEventListener("mouseover", () => {
    shuffleBtn.style.color = "#b8b8b8";
});

shuffleBtn.addEventListener("mouseout", () => {
    if(shuffleBtn.dataset.active == "false"){
        shuffleBtn.style.color = "black";
    }
    else{
        shuffleBtn.style.color = "#8c8c8c";
    }
});

function volumeUp(){
    if(volumeBar.value < 100){
        currentTrack.volume = currentTrack.volume + 0.05;
        volumeBar.value = parseInt(volumeBar.value) + 5;
    }
};

function volumeDown(){
    if(volumeBar.value > 0){
        currentTrack.volume = currentTrack.volume - 0.05;
        volumeBar.value = parseInt(volumeBar.value) - 5;
    }
};

// ##### Mobile Menu Btn #####
var menuButton = document.getElementById("mobile-menu-btn");
menuButton.addEventListener("click", (e) => {
    let sideBar = document.getElementById("side-bar");
    if(menuButton.dataset.active == "false"){
        menuButton.dataset.active = "true";
        sideBar.style.display = "block";
    }
    else{
        menuButton.dataset.active = "false";
        sideBar.style.display = "none";
    }
});

// ################## Keypress functionality ##################
document.addEventListener("keypress", function(e){
    if(e.code == "KeyB"){
        backBtn.click();
    }
    else if(e.code == "KeyN"){
        forwardBtn.click();
    }
    else if(e.code == "Space"){
        playPauseBtn.click();
    }
    else if(e.code == "KeyL"){
        loopBtn.click();
    }
    else if(e.code == "KeyS"){
        shuffleBtn.click();
    }
});