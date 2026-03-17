/**
 * Storage Module - localStorage Management
 */

const Storage = {
    STORAGE_KEY: 'iptv_app_data',
    
    /**
     * Get all app data from localStorage
     */
    getData() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            if (data) {
                return JSON.parse(data);
            }
        } catch (e) {
            console.error('Storage.getData error:', e);
        }
        return this.getDefaultData();
    },
    
    /**
     * Get default data structure
     */
    getDefaultData() {
        return {
            channels: [],
            customChannels: [],
            favorites: [],
            recent: [],
            settings: {
                defaultCountry: 'taiwan',
                autoplay: true,
                volume: 0.8
            },
            lastUpdated: null
        };
    },
    
    /**
     * Save data to localStorage
     */
    saveData(data) {
        try {
            data.lastUpdated = new Date().toISOString();
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify(data));
            return true;
        } catch (e) {
            console.error('Storage.saveData error:', e);
            return false;
        }
    },
    
    /**
     * Get all channels (built-in + custom)
     */
    getAllChannels() {
        const data = this.getData();
        return [...data.channels, ...data.customChannels];
    },
    
    /**
     * Get favorite channels
     */
    getFavoriteChannels() {
        const data = this.getData();
        const allChannels = this.getAllChannels();
        return allChannels.filter(ch => data.favorites.includes(ch.id));
    },
    
    /**
     * Get custom channels
     */
    getCustomChannels() {
        const data = this.getData();
        return data.customChannels;
    },
    
    /**
     * Add a custom channel
     */
    addCustomChannel(channel) {
        const data = this.getData();
        const newChannel = {
            ...channel,
            id: 'custom_' + Date.now(),
            isCustom: true,
            isFavorite: false
        };
        data.customChannels.push(newChannel);
        return this.saveData(data) ? newChannel : null;
    },
    
    /**
     * Update a custom channel
     */
    updateCustomChannel(id, updates) {
        const data = this.getData();
        const index = data.customChannels.findIndex(ch => ch.id === id);
        if (index !== -1) {
            data.customChannels[index] = { ...data.customChannels[index], ...updates };
            return this.saveData(data);
        }
        return false;
    },
    
    /**
     * Delete a custom channel
     */
    deleteCustomChannel(id) {
        const data = this.getData();
        data.customChannels = data.customChannels.filter(ch => ch.id !== id);
        data.favorites = data.favorites.filter(favId => favId !== id);
        return this.saveData(data);
    },
    
    /**
     * Toggle favorite status
     */
    toggleFavorite(channelId) {
        const data = this.getData();
        const index = data.favorites.indexOf(channelId);
        if (index === -1) {
            data.favorites.push(channelId);
        } else {
            data.favorites.splice(index, 1);
        }
        this.saveData(data);
        return index === -1; // returns true if now favorite
    },
    
    /**
     * Check if channel is favorite
     */
    isFavorite(channelId) {
        const data = this.getData();
        return data.favorites.includes(channelId);
    },
    
    /**
     * Add to recent channels
     */
    addRecent(channelId) {
        const data = this.getData();
        // Remove if already exists
        data.recent = data.recent.filter(id => id !== channelId);
        // Add to front
        data.recent.unshift(channelId);
        // Keep only last 10
        data.recent = data.recent.slice(0, 10);
        this.saveData(data);
    },
    
    /**
     * Get recent channels
     */
    getRecentChannels() {
        const data = this.getData();
        const allChannels = this.getAllChannels();
        return data.recent
            .map(id => allChannels.find(ch => ch.id === id))
            .filter(ch => ch !== undefined);
    },
    
    /**
     * Get settings
     */
    getSettings() {
        const data = this.getData();
        return data.settings;
    },
    
    /**
     * Update settings
     */
    updateSettings(updates) {
        const data = this.getData();
        data.settings = { ...data.settings, ...updates };
        return this.saveData(data);
    },
    
    /**
     * Set built-in channels (from M3U8)
     */
    setChannels(channels) {
        const data = this.getData();
        // Keep custom channels, update built-in
        data.channels = channels;
        return this.saveData(data);
    },
    
    /**
     * Clear all favorites
     */
    clearFavorites() {
        const data = this.getData();
        data.favorites = [];
        return this.saveData(data);
    },
    
    /**
     * Reset all data
     */
    resetAll() {
        localStorage.removeItem(this.STORAGE_KEY);
        return this.getDefaultData();
    },
    
    /**
     * Get channels by country
     */
    getChannelsByCountry(country) {
        const allChannels = this.getAllChannels();
        if (country === 'all') return allChannels;
        return allChannels.filter(ch => ch.country === country);
    },
    
    /**
     * Get channels by category
     */
    getChannelsByCategory(category) {
        const allChannels = this.getAllChannels();
        if (category === 'all') return allChannels;
        return allChannels.filter(ch => ch.category === category);
    },
    
    /**
     * Get channels by country and category
     */
    getFilteredChannels(country, category) {
        let channels = this.getAllChannels();
        
        if (country && country !== 'all') {
            channels = channels.filter(ch => ch.country === country);
        }
        
        if (category && category !== 'all') {
            channels = channels.filter(ch => ch.category === category);
        }
        
        return channels;
    },
    
    /**
     * Search channels
     */
    searchChannels(query) {
        const allChannels = this.getAllChannels();
        const lowerQuery = query.toLowerCase();
        return allChannels.filter(ch => 
            ch.name.toLowerCase().includes(lowerQuery) ||
            ch.country.toLowerCase().includes(lowerQuery) ||
            ch.category.toLowerCase().includes(lowerQuery)
        );
    },
    
    /**
     * Get unique countries from all channels
     */
    getCountries() {
        const allChannels = this.getAllChannels();
        const countries = [...new Set(allChannels.map(ch => ch.country))];
        return countries.sort();
    },
    
    /**
     * Get categories for a specific country
     */
    getCategoriesForCountry(country) {
        const channels = country === 'all' 
            ? this.getAllChannels() 
            : this.getChannelsByCountry(country);
        const categories = [...new Set(channels.map(ch => ch.category))];
        return categories.sort();
    }
};

// Export for use in other modules
window.Storage = Storage;
