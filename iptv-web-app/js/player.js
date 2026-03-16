/**
 * Player Module - HLS Video Player Control
 */

const Player = {
    video: null,
    hls: null,
    currentChannel: null,
    isPlaying: false,
    isMuted: false,
    volume: 0.8,
    reconnectAttempts: 0,
    maxReconnectAttempts: 3,
    
    /**
     * Initialize player
     */
    init(videoElement) {
        this.video = videoElement;
        this.setupEventListeners();
    },
    
    /**
     * Setup video event listeners
     */
    setupEventListeners() {
        if (!this.video) return;
        
        // Play/Pause events
        this.video.addEventListener('play', () => {
            this.isPlaying = true;
            this.onPlayStateChange?.(true);
        });
        
        this.video.addEventListener('pause', () => {
            this.isPlaying = false;
            this.onPlayStateChange?.(false);
        });
        
        // Loading events
        this.video.addEventListener('waiting', () => {
            this.onLoading?.(true);
        });
        
        this.video.addEventListener('canplay', () => {
            this.onLoading?.(false);
        });
        
        // Error handling
        this.video.addEventListener('error', (e) => {
            this.handleError(e);
        });
        
        // Volume change
        this.video.addEventListener('volumechange', () => {
            this.onVolumeChange?.(this.video.volume);
        });
        
        // Time update for progress
        this.video.addEventListener('timeupdate', () => {
            this.onTimeUpdate?.(this.video.currentTime, this.video.duration);
        });
        
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            this.handleKeyboard(e);
        });
    },
    
    /**
     * Play a channel
     */
    async play(channel) {
        if (!channel || !channel.url) {
            console.error('Invalid channel:', channel);
            return false;
        }
        
        this.currentChannel = channel;
        this.reconnectAttempts = 0;
        
        // Stop current playback
        this.stop();
        
        // Show loading
        this.onLoading?.(true);
        
        try {
            // Check if HLS is supported
            if (Hls.isSupported()) {
                // Use HLS.js for browsers that don't support HLS natively
                this.hls = new Hls({
                    maxLoadingDelay: 4,
                    maxBufferLength: 30,
                    maxMaxBufferLength: 60,
                    enableWorker: true,
                    lowLatencyMode: false
                });
                
                this.hls.loadSource(channel.url);
                this.hls.attachMedia(this.video);
                
                this.hls.on(Hls.Events.MANIFEST_PARSED, () => {
                    this.onReady?.();
                    this.video.play().catch(e => {
                        console.error('Auto-play failed:', e);
                    });
                });
                
                this.hls.on(Hls.Events.ERROR, (event, data) => {
                    if (data.fatal) {
                        this.handleHlsError(data);
                    }
                });
                
            } else if (this.video.canPlayType('application/vnd.apple.mpegurl')) {
                // Native HLS support (Safari)
                this.video.src = channel.url;
                this.video.addEventListener('loadedmetadata', () => {
                    this.onReady?.();
                    this.video.play().catch(e => {
                        console.error('Auto-play failed:', e);
                    });
                });
                
            } else {
                // Try direct playback for other formats
                this.video.src = channel.url;
            }
            
            return true;
        } catch (e) {
            console.error('Play error:', e);
            this.onError?.(e.message);
            return false;
        }
    },
    
    /**
     * Handle HLS.js errors
     */
    handleHlsError(data) {
        switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
                console.error('Network error, trying to recover...');
                this.hls.startLoad();
                break;
            case Hls.ErrorTypes.MEDIA_ERROR:
                console.error('Media error, trying to recover...');
                this.hls.recoverMediaError();
                break;
            default:
                this.handleError(data);
                break;
        }
    },
    
    /**
     * Handle general errors
     */
    handleError(e) {
        console.error('Player error:', e);
        
        // Try to reconnect
        if (this.reconnectAttempts < this.maxReconnectAttempts && this.currentChannel) {
            this.reconnectAttempts++;
            console.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                if (this.currentChannel) {
                    this.play(this.currentChannel);
                }
            }, 2000 * this.reconnectAttempts);
        } else {
            this.onError?.(e.message || '播放失敗，請嘗試其他頻道');
        }
    },
    
    /**
     * Stop playback
     */
    stop() {
        if (this.hls) {
            this.hls.destroy();
            this.hls = null;
        }
        
        this.video.src = '';
        this.video.removeAttribute('src');
        this.currentChannel = null;
        this.isPlaying = false;
    },
    
    /**
     * Toggle play/pause
     */
    togglePlay() {
        if (this.video.paused) {
            this.video.play();
        } else {
            this.video.pause();
        }
    },
    
    /**
     * Play
     */
    playVideo() {
        this.video.play();
    },
    
    /**
     * Pause
     */
    pauseVideo() {
        this.video.pause();
    },
    
    /**
     * Set volume
     */
    setVolume(value) {
        this.volume = Math.max(0, Math.min(1, value));
        this.video.volume = this.volume;
        if (this.volume > 0) {
            this.video.muted = false;
            this.isMuted = false;
        }
    },
    
    /**
     * Toggle mute
     */
    toggleMute() {
        this.video.muted = !this.video.muted;
        this.isMuted = this.video.muted;
        return this.isMuted;
    },
    
    /**
     * Seek to position
     */
    seek(time) {
        if (this.video.duration) {
            this.video.currentTime = time;
        }
    },
    
    /**
     * Seek forward
     */
    seekForward(seconds = 10) {
        this.seek(this.video.currentTime + seconds);
    },
    
    /**
     * Seek backward
     */
    seekBackward(seconds = 10) {
        this.seek(this.video.currentTime - seconds);
    },
    
    /**
     * Enter fullscreen
     */
    async enterFullscreen() {
        try {
            if (this.video.requestFullscreen) {
                await this.video.requestFullscreen();
            } else if (this.video.webkitEnterFullscreen) {
                await this.video.webkitEnterFullscreen();
            }
        } catch (e) {
            console.error('Fullscreen error:', e);
        }
    },
    
    /**
     * Exit fullscreen
     */
    async exitFullscreen() {
        try {
            if (document.exitFullscreen) {
                await document.exitFullscreen();
            } else if (document.webkitExitFullscreen) {
                await document.webkitExitFullscreen();
            }
        } catch (e) {
            console.error('Exit fullscreen error:', e);
        }
    },
    
    /**
     * Toggle fullscreen
     */
    async toggleFullscreen() {
        if (document.fullscreenElement) {
            await this.exitFullscreen();
        } else {
            await this.enterFullscreen();
        }
    },
    
    /**
     * Enter picture-in-picture
     */
    async enterPip() {
        try {
            if (this.video.requestPictureInPicture) {
                await this.video.requestPictureInPicture();
            }
        } catch (e) {
            console.error('PIP error:', e);
        }
    },
    
    /**
     * Handle keyboard controls
     */
    handleKeyboard(e) {
        // Only handle if video is focused or no input is focused
        const tag = e.target.tagName.toLowerCase();
        if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) {
            return;
        }
        
        switch (e.key) {
            case ' ':
            case 'k':
                e.preventDefault();
                this.togglePlay();
                break;
            case 'ArrowLeft':
            case 'j':
                e.preventDefault();
                this.seekBackward(10);
                break;
            case 'ArrowRight':
            case 'l':
                e.preventDefault();
                this.seekForward(10);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.setVolume(this.volume + 0.1);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.setVolume(this.volume - 0.1);
                break;
            case 'm':
                e.preventDefault();
                this.toggleMute();
                break;
            case 'f':
                e.preventDefault();
                this.toggleFullscreen();
                break;
            case 'p':
                e.preventDefault();
                this.enterPip();
                break;
        }
    },
    
    /**
     * Get current playback time
     */
    getCurrentTime() {
        return this.video.currentTime;
    },
    
    /**
     * Get video duration
     */
    getDuration() {
        return this.video.duration || 0;
    },
    
    /**
     * Check if playing
     */
    getIsPlaying() {
        return this.isPlaying;
    }
};

// Export for use in other modules
window.Player = Player;
