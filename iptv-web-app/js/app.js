/**
 * IPTV Web App - Main Application
 */

const App = {
    // State
    currentView: 'all', // 'all', 'favorites', 'custom'
    currentCountry: 'all',
    currentCategory: 'all',
    searchQuery: '',
    isLoading: true,
    
    // DOM Elements
    elements: {},
    
    /**
     * Initialize the app
     */
    async init() {
        console.log('Initializing IPTV Web App...');
        
        // Cache DOM elements
        this.cacheElements();
        
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Initialize player
        Player.init(this.elements.videoPlayer);
        
        // Setup player callbacks
        this.setupPlayerCallbacks();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Load channels
        await this.loadChannels();
        
        // Render UI
        this.render();
        
        // Apply settings
        this.applySettings();
        
        console.log('IPTV Web App initialized!');
    },
    
    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.elements = {
            // Header
            menuBtn: document.getElementById('menuBtn'),
            searchInput: document.getElementById('searchInput'),
            settingsBtn: document.getElementById('settingsBtn'),
            
            // Sidebar
            sidebar: document.getElementById('sidebar'),
            allCount: document.getElementById('allCount'),
            favCount: document.getElementById('favCount'),
            customCount: document.getElementById('customCount'),
            countryList: document.getElementById('countryList'),
            
            // Player
            videoPlayer: document.getElementById('videoPlayer'),
            playerOverlay: document.getElementById('playerOverlay'),
            playBtnLarge: document.getElementById('playBtnLarge'),
            playerControls: document.getElementById('playerControls'),
            playPauseBtn: document.getElementById('playPauseBtn'),
            volumeBtn: document.getElementById('volumeBtn'),
            volumeSlider: document.getElementById('volumeSlider'),
            currentChannel: document.getElementById('currentChannel'),
            qualityBadge: document.getElementById('qualityBadge'),
            pipBtn: document.getElementById('pipBtn'),
            fullscreenBtn: document.getElementById('fullscreenBtn'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            
            // Channel Grid
            sectionTitle: document.getElementById('sectionTitle'),
            categoryTabs: document.getElementById('categoryTabs'),
            channelGrid: document.getElementById('channelGrid'),
            emptyState: document.getElementById('emptyState'),
            loadingChannels: document.getElementById('loadingChannels'),
            
            // Modals
            settingsModal: document.getElementById('settingsModal'),
            closeSettings: document.getElementById('closeSettings'),
            addChannelModal: document.getElementById('addChannelModal'),
            closeAddChannel: document.getElementById('closeAddChannel'),
            channelForm: document.getElementById('channelForm'),
            cancelChannel: document.getElementById('cancelChannel'),
            
            // Settings
            autoplayToggle: document.getElementById('autoplayToggle'),
            defaultVolume: document.getElementById('defaultVolume'),
            clearFavorites: document.getElementById('clearFavorites'),
            resetChannels: document.getElementById('resetChannels'),
            
            // Toast
            toastContainer: document.getElementById('toastContainer')
        };
    },
    
    /**
     * Setup player callbacks
     */
    setupPlayerCallbacks() {
        Player.onPlayStateChange = (isPlaying) => {
            this.updatePlayButton(isPlaying);
            if (isPlaying) {
                this.elements.playerOverlay.classList.add('hidden');
            }
        };
        
        Player.onLoading = (isLoading) => {
            if (isLoading) {
                this.elements.loadingIndicator.classList.add('visible');
            } else {
                this.elements.loadingIndicator.classList.remove('visible');
            }
        };
        
        Player.onError = (message) => {
            this.showToast(message, 'error');
            this.elements.playerOverlay.classList.remove('hidden');
        };
        
        Player.onVolumeChange = (volume) => {
            this.elements.volumeSlider.value = volume;
            this.updateVolumeIcon(volume);
        };
    },
    
    /**
     * Setup event listeners
     */
    setupEventListeners() {
        // Menu button
        this.elements.menuBtn.addEventListener('click', () => {
            this.elements.sidebar.classList.toggle('open');
        });
        
        // Search
        this.elements.searchInput.addEventListener('input', (e) => {
            this.searchQuery = e.target.value;
            this.renderChannels();
        });
        
        // Settings button
        this.elements.settingsBtn.addEventListener('click', () => {
            this.openSettings();
        });
        
        // Player controls
        this.elements.playBtnLarge.addEventListener('click', () => {
            if (Player.currentChannel) {
                Player.playVideo();
            }
        });
        
        this.elements.playPauseBtn.addEventListener('click', () => {
            Player.togglePlay();
        });
        
        this.elements.volumeBtn.addEventListener('click', () => {
            const muted = Player.toggleMute();
            this.updateVolumeIcon(muted ? 0 : Player.volume);
        });
        
        this.elements.volumeSlider.addEventListener('input', (e) => {
            Player.setVolume(parseFloat(e.target.value));
        });
        
        this.elements.pipBtn.addEventListener('click', () => {
            Player.enterPip();
        });
        
        this.elements.fullscreenBtn.addEventListener('click', () => {
            Player.toggleFullscreen();
        });
        
        // Show controls on mouse move
        let controlsTimeout;
        this.elements.videoPlayer.addEventListener('mousemove', () => {
            this.elements.playerControls.classList.add('visible');
            clearTimeout(controlsTimeout);
            controlsTimeout = setTimeout(() => {
                if (Player.isPlaying) {
                    this.elements.playerControls.classList.remove('visible');
                }
            }, 3000);
        });
        
        // Settings modal
        this.elements.closeSettings.addEventListener('click', () => {
            this.closeSettings();
        });
        
        this.elements.settingsModal.querySelector('.modal-backdrop').addEventListener('click', () => {
            this.closeSettings();
        });
        
        // Autoplay toggle
        this.elements.autoplayToggle.addEventListener('change', (e) => {
            Storage.updateSettings({ autoplay: e.target.checked });
        });
        
        // Volume slider
        this.elements.defaultVolume.addEventListener('input', (e) => {
            Storage.updateSettings({ volume: parseFloat(e.target.value) });
        });
        
        // Clear favorites
        this.elements.clearFavorites.addEventListener('click', () => {
            if (confirm('確定要清除所有收藏嗎？')) {
                Storage.clearFavorites();
                this.render();
                this.showToast('已清除所有收藏', 'success');
            }
        });
        
        // Reset channels
        this.elements.resetChannels.addEventListener('click', () => {
            if (confirm('確定要重置頻道列表嗎？自訂頻道將被保留。')) {
                this.loadChannels(true);
                this.showToast('已重置頻道列表', 'success');
            }
        });
        
        // Add channel modal
        this.elements.closeAddChannel.addEventListener('click', () => {
            this.closeAddChannel();
        });
        
        this.elements.addChannelModal.querySelector('.modal-backdrop').addEventListener('click', () => {
            this.closeAddChannel();
        });
        
        this.elements.cancelChannel.addEventListener('click', () => {
            this.closeAddChannel();
        });
        
        this.elements.channelForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveChannel();
        });
        
        // Nav items (delegated)
        document.querySelector('.sidebar-nav').addEventListener('click', (e) => {
            const navItem = e.target.closest('.nav-item');
            if (navItem) {
                const view = navItem.dataset.view;
                if (view) {
                    this.setView(view);
                }
            }
            
            const countryItem = e.target.closest('.country-item');
            if (countryItem) {
                const country = countryItem.dataset.country;
                if (country !== undefined) {
                    this.setCountry(country);
                }
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Escape to close modals
            if (e.key === 'Escape') {
                this.closeSettings();
                this.closeAddChannel();
            }
        });
    },
    
    /**
     * Load channels from M3U8
     */
    async loadChannels(forceReload = false) {
        this.isLoading = true;
        
        // Check if we have cached channels
        const data = Storage.getData();
        if (!forceReload && data.channels && data.channels.length > 0) {
            console.log('Using cached channels:', data.channels.length);
            this.isLoading = false;
            return;
        }
        
        try {
            console.log('Loading channels from M3U8...');
            const url = 'https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8';
            const channels = await M3U8Parser.fetchAndParse(url);
            
            console.log('Loaded channels:', channels.length);
            Storage.setChannels(channels);
            
            this.showToast(`已載入 ${channels.length} 個頻道`, 'success');
        } catch (e) {
            console.error('Failed to load channels:', e);
            this.showToast('載入頻道失敗，請檢查網路連線', 'error');
            
            // Load sample channels for offline testing
            this.loadSampleChannels();
        }
        
        this.isLoading = false;
    },
    
    /**
     * Load sample channels for testing
     */
    loadSampleChannels() {
        const sampleChannels = [
            { id: 'sample_1', name: '台視', url: 'https://example.com/ttv.m3u8', country: 'taiwan', category: 'news', isCustom: false },
            { id: 'sample_2', name: '中視', url: 'https://example.com/ctv.m3u8', country: 'taiwan', category: 'entertainment', isCustom: false },
            { id: 'sample_3', name: '華視', url: 'https://example.com/cts.m3u8', country: 'taiwan', category: 'news', isCustom: false },
        ];
        Storage.setChannels(sampleChannels);
    },
    
    /**
     * Apply settings
     */
    applySettings() {
        const settings = Storage.getSettings();
        
        this.elements.autoplayToggle.checked = settings.autoplay;
        this.elements.defaultVolume.value = settings.volume;
        Player.setVolume(settings.volume);
    },
    
    /**
     * Render UI
     */
    render() {
        this.renderSidebar();
        this.renderCategories();
        this.renderChannels();
    },
    
    /**
     * Render sidebar
     */
    renderSidebar() {
        const allChannels = Storage.getAllChannels();
        const favorites = Storage.getFavoriteChannels();
        const custom = Storage.getCustomChannels();
        
        this.elements.allCount.textContent = allChannels.length;
        this.elements.favCount.textContent = favorites.length;
        this.elements.customCount.textContent = custom.length;
        
        // Render countries
        const countries = Storage.getCountries();
        const countryListHtml = countries.map(country => {
            const channels = Storage.getChannelsByCountry(country);
            const flag = M3U8Parser.getCountryFlag(country);
            const name = M3U8Parser.getCountryName(country);
            const isActive = this.currentCountry === country;
            
            return `
                <div class="country-item ${isActive ? 'active' : ''}" data-country="${country}">
                    <span class="country-flag">${flag}</span>
                    <span class="country-name">${name}</span>
                    <span class="country-count">${channels.length}</span>
                </div>
            `;
        }).join('');
        
        this.elements.countryList.innerHTML = countryListHtml;
        
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === this.currentView) {
                item.classList.add('active');
            }
        });
    },
    
    /**
     * Render category tabs
     */
    renderCategories() {
        const categories = Storage.getCategoriesForCountry(this.currentCountry);
        
        const tabsHtml = ['all', ...categories].map(cat => {
            const isActive = this.currentCategory === cat;
            const name = cat === 'all' ? '全部' : M3U8Parser.getCategoryName(cat);
            
            return `<button class="category-tab ${isActive ? 'active' : ''}" data-category="${cat}">${name}</button>`;
        }).join('');
        
        this.elements.categoryTabs.innerHTML = tabsHtml;
        
        // Add click handlers
        this.elements.categoryTabs.querySelectorAll('.category-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.setCategory(tab.dataset.category);
            });
        });
    },
    
    /**
     * Render channel grid
     */
    renderChannels() {
        // Show loading state
        if (this.isLoading) {
            this.elements.loadingChannels.classList.add('visible');
            this.elements.channelGrid.innerHTML = '';
            this.elements.emptyState.classList.remove('visible');
            return;
        }
        
        this.elements.loadingChannels.classList.remove('visible');
        
        let channels;
        
        // Get channels based on view
        switch (this.currentView) {
            case 'favorites':
                channels = Storage.getFavoriteChannels();
                this.elements.sectionTitle.textContent = '我的最愛';
                break;
            case 'custom':
                channels = Storage.getCustomChannels();
                this.elements.sectionTitle.textContent = '自訂頻道';
                break;
            default:
                channels = Storage.getFilteredChannels(this.currentCountry, this.currentCategory);
                this.elements.sectionTitle.textContent = this.currentCountry === 'all' 
                    ? '所有頻道' 
                    : M3U8Parser.getCountryName(this.currentCountry);
        }
        
        // Apply search filter
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            channels = channels.filter(ch => 
                ch.name.toLowerCase().includes(query) ||
                ch.country.toLowerCase().includes(query) ||
                ch.category.toLowerCase().includes(query)
            );
        }
        
        // Show/hide empty state
        if (channels.length === 0) {
            this.elements.channelGrid.innerHTML = '';
            this.elements.emptyState.classList.add('visible');
        } else {
            this.elements.emptyState.classList.remove('visible');
            
            // Render channel cards
            const gridHtml = channels.map(channel => {
                const isFavorite = Storage.isFavorite(channel.id);
                const isPlaying = Player.currentChannel?.id === channel.id;
                
                return this.renderChannelCard(channel, isFavorite, isPlaying);
            }).join('');
            
            this.elements.channelGrid.innerHTML = gridHtml;
            
            // Add click handlers
            this.elements.channelGrid.querySelectorAll('.channel-card').forEach(card => {
                card.addEventListener('click', (e) => {
                    if (!e.target.closest('.channel-favorite')) {
                        const channelId = card.dataset.id;
                        const channel = Storage.getAllChannels().find(ch => ch.id === channelId);
                        if (channel) {
                            this.playChannel(channel);
                        }
                    }
                });
                
                const favBtn = card.querySelector('.channel-favorite');
                if (favBtn) {
                    favBtn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const channelId = card.dataset.id;
                        this.toggleFavorite(channelId);
                    });
                }
            });
        }
    },
    
    /**
     * Render a single channel card
     */
    renderChannelCard(channel, isFavorite, isPlaying) {
        const logoHtml = channel.logo 
            ? `<img src="${channel.logo}" alt="${channel.name}" onerror="this.parentElement.innerHTML='<span class=\\'placeholder\\'>📺</span>'">`
            : `<span class="placeholder">📺</span>`;
        
        const countryFlag = M3U8Parser.getCountryFlag(channel.country);
        const categoryName = M3U8Parser.getCategoryName(channel.category);
        
        return `
            <div class="channel-card ${isPlaying ? 'playing' : ''}" data-id="${channel.id}">
                <button class="channel-favorite ${isFavorite ? 'active' : ''}" aria-label="收藏">
                    <i data-lucide="heart"></i>
                </button>
                <div class="channel-logo">
                    ${logoHtml}
                </div>
                <div class="channel-name" title="${channel.name}">${channel.name}</div>
                <div class="channel-info">
                    <span class="channel-badge">${countryFlag} ${categoryName}</span>
                </div>
            </div>
        `;
    },
    
    /**
     * Play a channel
     */
    playChannel(channel) {
        console.log('Playing channel:', channel.name);
        
        // Update UI
        this.elements.currentChannel.textContent = channel.name;
        this.elements.playerOverlay.classList.remove('hidden');
        
        // Play
        Player.play(channel);
        
        // Update channel grid
        this.renderChannels();
    },
    
    /**
     * Toggle favorite
     */
    toggleFavorite(channelId) {
        const isFavorite = Storage.toggleFavorite(channelId);
        
        // Update UI
        this.render();
        
        // Show toast
        this.showToast(
            isFavorite ? '已加入我的最愛' : '已移除我的最愛',
            'success'
        );
        
        // Animate heart
        const btn = document.querySelector(`.channel-card[data-id="${channelId}"] .channel-favorite`);
        if (btn) {
            btn.classList.add('animate-bounce');
            setTimeout(() => btn.classList.remove('animate-bounce'), 300);
        }
    },
    
    /**
     * Set current view
     */
    setView(view) {
        this.currentView = view;
        this.currentCountry = 'all';
        this.currentCategory = 'all';
        
        // Update nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === view) {
                item.classList.add('active');
            }
        });
        
        // Reset filters
        document.querySelectorAll('.country-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // Show add button for custom view
        if (view === 'custom') {
            this.showAddChannelButton();
        } else {
            this.hideAddChannelButton();
        }
        
        this.render();
    },
    
    /**
     * Set current country
     */
    setCountry(country) {
        this.currentCountry = country;
        this.currentCategory = 'all';
        
        // Update country items
        document.querySelectorAll('.country-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.country === country) {
                item.classList.add('active');
            }
        });
        
        // Reset view to all
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.view === 'all') {
                item.classList.add('active');
            }
        });
        this.currentView = 'all';
        
        this.renderCategories();
        this.renderChannels();
    },
    
    /**
     * Set current category
     */
    setCategory(category) {
        this.currentCategory = category;
        
        // Update tabs
        document.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.remove('active');
            if (tab.dataset.category === category) {
                tab.classList.add('active');
            }
        });
        
        this.renderChannels();
    },
    
    /**
     * Update play button icon
     */
    updatePlayButton(isPlaying) {
        const icon = isPlaying ? 'pause' : 'play';
        this.elements.playPauseBtn.innerHTML = `<i data-lucide="${icon}"></i>`;
        lucide.createIcons();
    },
    
    /**
     * Update volume icon
     */
    updateVolumeIcon(volume) {
        let icon = 'volume-2';
        if (volume === 0) {
            icon = 'volume-x';
        } else if (volume < 0.5) {
            icon = 'volume-1';
        }
        
        this.elements.volumeBtn.innerHTML = `<i data-lucide="${icon}"></i>`;
        lucide.createIcons();
    },
    
    /**
     * Open settings modal
     */
    openSettings() {
        this.elements.settingsModal.classList.add('visible');
    },
    
    /**
     * Close settings modal
     */
    closeSettings() {
        this.elements.settingsModal.classList.remove('visible');
    },
    
    /**
     * Show add channel button
     */
    showAddChannelButton() {
        // Add button to section header if not exists
        let addBtn = document.getElementById('addChannelBtn');
        if (!addBtn) {
            addBtn = document.createElement('button');
            addBtn.id = 'addChannelBtn';
            addBtn.className = 'btn btn-primary';
            addBtn.innerHTML = '<i data-lucide="plus"></i> 新增頻道';
            this.elements.sectionHeader = document.querySelector('.section-header');
            this.elements.sectionHeader.appendChild(addBtn);
            
            addBtn.addEventListener('click', () => {
                this.openAddChannel();
            });
            
            lucide.createIcons();
        }
        addBtn.style.display = 'flex';
    },
    
    /**
     * Hide add channel button
     */
    hideAddChannelButton() {
        const addBtn = document.getElementById('addChannelBtn');
        if (addBtn) {
            addBtn.style.display = 'none';
        }
    },
    
    /**
     * Open add channel modal
     */
    openAddChannel() {
        this.elements.addChannelModal.classList.add('visible');
        document.getElementById('channelName').focus();
    },
    
    /**
     * Close add channel modal
     */
    closeAddChannel() {
        this.elements.addChannelModal.classList.remove('visible');
        this.elements.channelForm.reset();
    },
    
    /**
     * Save channel from form
     */
    saveChannel() {
        const name = document.getElementById('channelName').value.trim();
        const url = document.getElementById('channelUrl').value.trim();
        const logo = document.getElementById('channelLogo').value.trim();
        const country = document.getElementById('channelCountry').value;
        const category = document.getElementById('channelCategory').value;
        
        if (!name || !url) {
            this.showToast('請填寫必填欄位', 'warning');
            return;
        }
        
        const channel = {
            name,
            url,
            logo: logo || null,
            country,
            category
        };
        
        const newChannel = Storage.addCustomChannel(channel);
        
        if (newChannel) {
            this.showToast('頻道已新增', 'success');
            this.closeAddChannel();
            this.render();
        } else {
            this.showToast('新增失敗', 'error');
        }
    },
    
    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        let icon = 'info';
        if (type === 'success') icon = 'check-circle';
        if (type === 'error') icon = 'x-circle';
        if (type === 'warning') icon = 'alert-triangle';
        
        toast.innerHTML = `
            <i data-lucide="${icon}"></i>
            <span class="toast-message">${message}</span>
        `;
        
        this.elements.toastContainer.appendChild(toast);
        lucide.createIcons();
        
        // Auto remove
        setTimeout(() => {
            toast.style.animation = 'toastIn 0.3s ease-out reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init().catch(e => {
        console.error('App initialization failed:', e);
    });
});

// Export for debugging
window.App = App;
