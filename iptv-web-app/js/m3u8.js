/**
 * M3U8 Parser Module - Parse M3U8 playlists
 */

const M3U8Parser = {
    /**
     * Fetch and parse M3U8 playlist
     */
    async fetchAndParse(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const text = await response.text();
            return this.parse(text, url);
        } catch (e) {
            console.error('M3U8 fetch error:', e);
            throw e;
        }
    },
    
    /**
     * Parse M3U8 content
     */
    parse(content, baseUrl = '') {
        const lines = content.split('\n');
        const channels = [];
        
        // Check if it's an extended M3U8
        const isExtended = lines[0] && lines[0].includes('#EXTM3U');
        
        if (!isExtended) {
            // Simple M3U8 - each line is a URL
            lines.forEach((line, index) => {
                const trimmed = line.trim();
                if (trimmed && !trimmed.startsWith('#')) {
                    channels.push({
                        id: `channel_${index}`,
                        name: `Channel ${index + 1}`,
                        url: trimmed,
                        country: 'other',
                        category: 'other',
                        logo: null,
                        isCustom: false,
                        isFavorite: false
                    });
                }
            });
        } else {
            // Extended M3U8 with #EXTINF
            let currentChannel = null;
            
            for (let i = 0; i < lines.length; i++) {
                const line = lines[i].trim();
                
                if (line.startsWith('#EXTINF:')) {
                    // Parse EXTINF metadata
                    const info = this.parseExtInf(line);
                    currentChannel = {
                        id: '',
                        name: info.name || 'Unknown',
                        url: '',
                        country: info.country || this.guessCountry(info.name),
                        category: this.guessCategory(info.name),
                        logo: info.logo,
                        isCustom: false,
                        isFavorite: false
                    };
                } else if (line && !line.startsWith('#') && currentChannel) {
                    // This is the URL
                    currentChannel.url = line;
                    currentChannel.id = this.generateChannelId(currentChannel.name);
                    
                    if (currentChannel.url) {
                        channels.push(currentChannel);
                    }
                    currentChannel = null;
                }
            }
        }
        
        return channels;
    },
    
    /**
     * Parse #EXTINF line
     */
    parseExtInf(line) {
        const result = {
            name: null,
            logo: null,
            duration: 0,
            country: null
        };
        
        // Extract duration
        const durationMatch = line.match(/#EXTINF:(\d+)/);
        if (durationMatch) {
            result.duration = parseInt(durationMatch[1], 10);
        }
        
        // Extract attributes
        const attrMatch = line.match(/,(.+)$/);
        if (attrMatch) {
            result.name = attrMatch[1].trim();
        }
        
        // Extract logo from tvg-logo
        const logoMatch = line.match(/tvg-logo="([^"]+)"/);
        if (logoMatch) {
            result.logo = logoMatch[1];
        }
        
        // Extract group from group-title
        const groupMatch = line.match(/group-title="([^"]+)"/);
        if (groupMatch) {
            result.group = groupMatch[1];
        }
        
        // Extract country from tvg-country
        const countryMatch = line.match(/tvg-country="([^"]+)"/);
        if (countryMatch) {
            result.country = this.mapCountryCode(countryMatch[1]);
        }
        
        return result;
    },
    
    /**
     * Map country code to country name
     */
    mapCountryCode(code) {
        const codeMap = {
            'TW': 'taiwan',
            'JP': 'japan',
            'KR': 'korea',
            'CN': 'china',
            'HK': 'hongkong',
            'SG': 'singapore',
            'US': 'usa',
            'UK': 'uk',
            'GB': 'uk'
        };
        return codeMap[code] || 'other';
    },
    
    /**
     * Generate channel ID from name
     */
    generateChannelId(name) {
        return 'ch_' + name
            .toLowerCase()
            .replace(/[^a-z0-9\u4e00-\u9fa5]/g, '_')
            .replace(/_+/g, '_')
            .replace(/^_|_$/g, '');
    },
    
    /**
     * Guess country from channel name
     */
    guessCountry(name) {
        const nameLower = name.toLowerCase();
        
        const countryKeywords = {
            taiwan: ['台灣', '台視', '中視', '華視', '民視', '公視', '東森', 'TVBS', '非凡', 'JET', '年代', '三立', '中天', 'TVGO', 'Taiwan'],
            japan: ['日本', 'NHK', 'TBS', '富士', '朝日', '東京', '日視', ' Japan', 'JAPAN'],
            korea: ['韓國', 'KBS', 'MBC', 'SBS', 'tvN', 'JTBC', ' Korea', 'KOREA'],
            china: ['中國', '央視', 'CCTV', '北京', '東方', '浙江', '江蘇', '湖南', ' China', 'CHINA'],
            usa: ['美國', 'ABC', 'CBS', 'NBC', 'FOX', 'CNN', 'MSNBC', 'USA', ' America'],
            uk: ['英國', 'BBC', 'ITV', 'Sky', ' Channel 4', ' UK', 'Britain']
        };
        
        for (const [country, keywords] of Object.entries(countryKeywords)) {
            for (const keyword of keywords) {
                if (nameLower.includes(keyword.toLowerCase())) {
                    return country;
                }
            }
        }
        
        return 'other';
    },
    
    /**
     * Guess category from channel name
     */
    guessCategory(name) {
        const nameLower = name.toLowerCase();
        
        const categoryKeywords = {
            news: ['新聞', 'news', '資訊', '情報', '時事'],
            entertainment: ['綜藝', '娛樂', 'entertainment', 'variety'],
            sports: ['體育', '運動', 'sports', '足球', '籃球', '棒球', 'MLB', 'NBA', 'NFL'],
            movie: ['電影', 'movie', 'cinema', '影城'],
            drama: ['戲劇', 'drama', '連續劇', '台劇', '陸劇', '韓劇', '日劇'],
            cartoon: ['卡通', '動畫', 'kids', 'children', 'アニメ'],
            music: ['音樂', 'music', 'MTV', '流行']
        };
        
        for (const [category, keywords] of Object.entries(categoryKeywords)) {
            for (const keyword of keywords) {
                if (nameLower.includes(keyword.toLowerCase())) {
                    return category;
                }
            }
        }
        
        return 'other';
    },
    
    /**
     * Get country display name
     */
    getCountryName(code) {
        const names = {
            taiwan: '台灣',
            japan: '日本',
            korea: '韓國',
            china: '中國',
            usa: '美國',
            uk: '英國',
            hongkong: '香港',
            singapore: '新加坡',
            other: '其他'
        };
        return names[code] || code;
    },
    
    /**
     * Get country flag emoji
     */
    getCountryFlag(code) {
        const flags = {
            taiwan: '🇹🇼',
            japan: '🇯🇵',
            korea: '🇰🇷',
            china: '🇨🇳',
            usa: '🇺🇸',
            uk: '🇬🇧',
            hongkong: '🇭🇰',
            singapore: '🇸🇬',
            other: '🌍'
        };
        return flags[code] || '🌍';
    },
    
    /**
     * Get category display name
     */
    getCategoryName(code) {
        const names = {
            news: '新聞',
            entertainment: '綜藝',
            sports: '體育',
            movie: '電影',
            drama: '戲劇',
            cartoon: '卡通',
            music: '音樂',
            other: '其他'
        };
        return names[code] || code;
    }
};

// Export for use in other modules
window.M3U8Parser = M3U8Parser;
