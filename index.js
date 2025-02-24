const image = document.getElementById('cover'),
    title = document.getElementById('music-title'),
    artist = document.getElementById('music-artist'),
    currentTimeEl = document.getElementById('current-time'),
    durationEl = document.getElementById('duration'),
    progress = document.getElementById('progress'),
    playerProgress = document.getElementById('player-progress'),
    prevBtn = document.getElementById('prev'),
    nextBtn = document.getElementById('next'),
    playBtn = document.getElementById('play'),
    background = document.getElementById('bg-img');

const music = new Audio();

const volumeSlider = document.getElementById('volume-slider');
const volumeIcon = document.getElementById('volume-icon');
const defaultCover = 'default.png';
let isMuted = false;


let musicIndex = 0;
let isPlaying = false;

function togglePlay() {
    if (isPlaying) {
        pauseMusic();
    } else {
        playMusic();
    }
}

function playMusic() {
    isPlaying = true;
    playBtn.classList.replace('fa-play', 'fa-pause');
    playBtn.setAttribute('title', 'Pause');
    music.volume = 0.4
    music.play();
}

function pauseMusic() {
    isPlaying = false;
    playBtn.classList.replace('fa-pause', 'fa-play');
    playBtn.setAttribute('title', 'Play');
    music.pause();
}

 function loadMusic(musicIndex) {
  music.src = songs[musicIndex].path;
  title.textContent = songs[musicIndex].displayName;
  artist.textContent = songs[musicIndex].artist;
  if (songs[musicIndex].cover === 'None') {
    image.src = defaultCover;
    background.src = defaultCover;
    } else {
    image.src = songs[musicIndex].cover;
    background.src = songs[musicIndex].cover;
    }
  music.currentTime = 0;
  music.onloadedmetadata = function() {
  durationEl.textContent = formatTime(music.duration);
  };
  music.onerror = function() {
  console.error("Failed to load audio source: " + music.src);
  };
  highlightCurrentSong();
  document.title = songs[musicIndex].artist + " - " +  songs[musicIndex].displayName;
  const faviconLink = document.getElementById('favicon');
  if (songs[musicIndex].cover === 'None') {
    faviconLink.href = defaultCover;
} else {
    faviconLink.href = songs[musicIndex].cover;
}
 }




let currentVolume = 1;

function setVolume() {
    if (!isMuted) {
        currentVolume = parseFloat(volumeSlider.value).toFixed(2);
        music.volume = currentVolume;
    }
}

function toggleMute() {
    if (isMuted) {
        isMuted = false;
        music.volume = currentVolume;
        volumeSlider.value = currentVolume;
        volumeIcon.classList = 'fa-solid fa-volume-high';
    } else {
        isMuted = true;
        music.volume = 0;
        volumeIcon.classList = 'fa-solid fa-volume-xmark';
    }
}

function updateVolumeIcon() {
    if (music.volume > 0.75) {
        volumeIcon.classList = 'fa-solid fa-volume-high';
    } else if (music.volume > 0.5) {
        volumeIcon.classList = 'fa-solid fa-volume-medium';
    } else if (music.volume > 0.25) {
        volumeIcon.classList = 'fa-solid fa-volume-low';
    } else if (music.volume > 0) {
        volumeIcon.classList = 'fa-solid fa-volume-off';
    } else {
        volumeIcon.classList = 'fa-solid fa-volume-xmark';
    }
}


volumeSlider.addEventListener('input', setVolume);
volumeIcon.addEventListener('click', () => {
    if (music.volume > 0) {
        music.volume = 0;
        volumeSlider.value = 0;
    } else {
        music.volume = 0.5;
        volumeSlider.value = 0.5;
    }
    updateVolumeIcon();
});



 function changeMusic(direction) {
  musicIndex = (musicIndex + direction + songs.length) % songs.length;
  loadMusic(musicIndex);
  playMusic();
 

  if (isMuted) {
  music.volume = 0;
  } else {
  music.volume = currentVolume;
  volumeSlider.value = currentVolume;
  }
  highlightCurrentSong(); // 현재 재생 중인 곡 강조
 }


function updateProgressBar() {
    const { duration, currentTime } = music;
    const progressPercent = (currentTime / duration) * 100;
    progress.style.width = `${progressPercent}%`;

    const formatTime = (time) => String(Math.floor(time)).padStart(2, '0');
    durationEl.textContent = `${formatTime(duration / 60)}:${formatTime(duration % 60)}`;
    currentTimeEl.textContent = `${formatTime(currentTime / 60)}:${formatTime(currentTime % 60)}`;
}

function setProgressBar(e) {
    const width = playerProgress.clientWidth;
    const clickX = e.offsetX;
    music.currentTime = (clickX / width) * music.duration;
}

const playlistContainer = document.getElementById('playlist');


function displayPlaylist() {
    const limitedSongs = songs.slice(0, 100); // 처음 100개의 곡만 선택
    playlistContainer.innerHTML = ''; // 기존 목록 초기화
    limitedSongs.forEach((song, index) => {
        const listItem = document.createElement('li');
        listItem.textContent = song.displayName;
        listItem.addEventListener('click', () => {
            musicIndex = index; // 클릭한 노래의 인덱스로 업데이트
            loadMusic(musicIndex); // 선택한 곡 로드
            playMusic(); // 음악 재생
            highlightCurrentSong(); // 재생 목록에서 현재 재생 중인 노래 강조 표시
        });
        playlistContainer.appendChild(listItem);
    });
}



 function highlightCurrentSong() {
  const playlistItems = document.querySelectorAll('.playlist li');
  playlistItems.forEach((item, index) => {
  if (index === musicIndex) {
  item.classList.add('active');
  } else {
  item.classList.remove('active');
  }
  });
 }

document.addEventListener('DOMContentLoaded', () => {
    loadMusic(musicIndex); // 첫 번째 노래 로드
    displayPlaylist(); // 재생 목록 생성
    highlightCurrentSong(); // 초기 강조 표시
   });
  

function formatTime(time) {
    let minutes = Math.floor(time / 60);
    let seconds = Math.floor(time - minutes * 60);
    if (seconds < 10) {
    seconds = "0" + seconds;
    }
    return minutes + ":" + seconds;
   }


playBtn.addEventListener('click', togglePlay);
prevBtn.addEventListener('click', () => changeMusic(-1));
nextBtn.addEventListener('click', () => changeMusic(1));
music.addEventListener('ended', () => changeMusic(1));
music.addEventListener('timeupdate', updateProgressBar);
playerProgress.addEventListener('click', setProgressBar);

loadMusic(songs[musicIndex]);