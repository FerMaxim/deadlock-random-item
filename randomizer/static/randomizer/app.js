document.addEventListener('DOMContentLoaded', () => {
    let itemsDatabase = [];
    let metaRules = {};
    let currentCategoryPrice = 'all';
    let currentCategoryType = 'all';
    let isRolling = false;
    let exhaustedItems = [];
    let currentTemperature = 2; // 1=META, 5=CHAOS

    const rollButton = document.getElementById('rollButton');
    const rollAllButton = document.getElementById('rollAllButton');
    const priceButtons = document.querySelectorAll('.price-group .btn');
    const typeButtons = document.querySelectorAll('.type-group .btn');
    const itemShowcase = document.getElementById('itemShowcase');
    const newGameBtn = document.getElementById('newGameBtn');
    const historyList = document.getElementById('historyList');
    const heroSelect = document.getElementById('heroSelect');
    const heroPortrait = document.getElementById('heroPortrait');
    const tempSlider = document.getElementById('tempSlider');
    const tempLabel = document.getElementById('tempLabel');
    const pips = document.querySelectorAll('.pip');

    const HERO_NAMES = {
        '1':'Infernus', '2':'Seven', '3':'Vindicta', '4':'Lady Geist',
        '6':'Abrams', '7':'Wraith', '8':'McGinnis', '10':'Paradox',
        '11':'Dynamo', '12':'Kelvin', '13':'Haze', '14':'Holliday',
        '15':'Pocket', '16':'Calico', '17':'Mirage', '18':'Bebop',
        '20':'Ivy', '25':'Grey Talon', '27':'Mo & Krill', '31':'Shiv',
        '35':'Viscous', '40':'Warden', '48':'Silver', '50':'Yamato',
        '52':'Lash', '58':'Vyper', '60':'Sinclair', '63':'Mina',
        '64':'Drifter', '65':'Venator', '66':'Victor', '67':'Paige',
        '69':'The Doorman', '72':'Billy', '76':'Graves', '77':'Apollo',
        '79':'Rem', '81':'Celeste'
    };
    const TEMP_CONFIG = [
        null,
        { label: 'META',   cls: 'temp-meta'   },
        { label: 'STABLE', cls: 'temp-normal'  },
        { label: 'MIXED',  cls: 'temp-mixed'   },
        { label: 'WILD',   cls: 'temp-wild'    },
        { label: 'CHAOS',  cls: 'temp-chaos'   },
    ];

    // Player States
    let playersState = {};
    let localPlayerNickname = 'Me';
    playersState[localPlayerNickname] = { items: [], hasBuild: false };
    
    // ── Load data ──
    Promise.all([
        fetch('/static/randomizer/data.json').then(r => r.json()),
        fetch('/static/randomizer/meta_rules.json').then(r => r.json()).catch(() => ({}))
    ]).then(([items, rules]) => {
        itemsDatabase = items;
        metaRules = rules;
        initHeroSelect();
        updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
    }).catch(err => {
        console.error('Failed to load data:', err);
        itemShowcase.innerHTML = `<div class="idle-state"><p style="color:red">Error loading item database.</p></div>`;
    });

    function initHeroSelect() {
        if (!heroSelect) return;
        heroSelect.innerHTML = '<option value="">Random Hero</option>';
        Object.entries(HERO_NAMES).sort((a,b) => a[1].localeCompare(b[1])).forEach(([id, name]) => {
            if (metaRules[id]) {
                const opt = document.createElement('option');
                opt.value = id; opt.textContent = name;
                heroSelect.appendChild(opt);
            }
        });
    }

    if (heroSelect) {
        heroSelect.addEventListener('change', () => {
            const id = heroSelect.value;
            if (!heroPortrait) return;
            if (id) {
                heroPortrait.innerHTML = `<img src="/static/randomizer/images/heroes/${id}.png" onerror="this.parentNode.innerHTML='<span>${HERO_NAMES[id]?.[0]||'?'}</span>'">`;
                heroPortrait.classList.add('has-hero');
            } else {
                heroPortrait.innerHTML = '<span>?</span>';
                heroPortrait.classList.remove('has-hero');
            }
        });
    }

    // ── Temperature slider ──
    function updateTemp(val) {
        currentTemperature = val;
        const cfg = TEMP_CONFIG[val];
        if (tempLabel) {
            tempLabel.textContent = cfg.label;
            tempLabel.className = 'temp-badge ' + cfg.cls;
        }
        pips.forEach(p => {
            p.classList.toggle('active', parseInt(p.dataset.t) <= val);
        });
    }
    if (tempSlider) {
        tempSlider.addEventListener('input', () => updateTemp(parseInt(tempSlider.value)));
        updateTemp(2);
    }

    // temperature → diversity (0.1 META … 1.0 CHAOS)
    function tempToDiversity(t) { return 0.1 + (t - 1) * 0.225; }

    // 2. Category Selection (Price)
    priceButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if(isRolling) return;
            priceButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategoryPrice = e.currentTarget.dataset.price;
        });
    });

    // Category Selection (Type)
    typeButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            if(isRolling) return;
            typeButtons.forEach(b => b.classList.remove('active'));
            e.currentTarget.classList.add('active');
            currentCategoryType = e.currentTarget.dataset.type;
        });
    });

    // ── Reset ──
    if (newGameBtn) {
        newGameBtn.addEventListener('click', () => {
            if (isRolling) return;
            exhaustedItems = [];
            if (historyList) historyList.innerHTML = '';
            playersState[localPlayerNickname] = { items: [], hasBuild: false };
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
            itemShowcase.innerHTML = `<div class="idle-state"><div class="scanner-line"></div><div class="occult-rune"></div><p>AWAITING INPUT...</p></div>`;
            const abilityPathContainer = document.getElementById('abilityPath');
            if (abilityPathContainer) abilityPathContainer.innerHTML = '';
            // Broadcast reset to party
            if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                partySocket.send(JSON.stringify({ type: 'reset', nickname: myNickname }));
            }
        });
    }

    // 3. Roll Logic
    rollButton.addEventListener('click', () => {
        if (isRolling || itemsDatabase.length === 0) return;
        
        // Count how many active items we already have
        let activeCount = itemsDatabase.filter(i => exhaustedItems.includes(i.id) && i.isActive).length;
        const maxActiveReached = activeCount >= 4;
        
        // Filter items by price, type, and exclude exhausted ones
        let pool = itemsDatabase.filter(item => {
            const matchPrice = currentCategoryPrice === 'all' || item.price == currentCategoryPrice;
            const matchType = currentCategoryType === 'all' || item.category === currentCategoryType;
            const notExhausted = !exhaustedItems.includes(item.id);
            const activeLimitOk = !maxActiveReached || !item.isActive;
            return matchPrice && matchType && notExhausted && activeLimitOk;
        });

        if (pool.length === 0) {
            if (maxActiveReached) {
                alert('No items available! You have reached the max active items limit.');
            } else {
                alert('Items in this category have run out!');
            }
            return;
        }

        startRollAnimation(pool);
    });

    if (rollAllButton) {
        rollAllButton.addEventListener('click', () => {
            if (isRolling || itemsDatabase.length === 0) return;
            
            let currentItemsCount = playersState[localPlayerNickname].items.length;
            let itemsNeeded = 15 - currentItemsCount;
            if (itemsNeeded <= 0) return;

            let pickedItems = [];

            for (let i = 0; i < itemsNeeded; i++) {
                let activeCount = itemsDatabase.filter(item => exhaustedItems.includes(item.id) && item.isActive).length;
                const maxActiveReached = activeCount >= 4;
                
                let pool = itemsDatabase.filter(item => {
                    const matchPrice = currentCategoryPrice === 'all' || item.price == currentCategoryPrice;
                    const matchType = currentCategoryType === 'all' || item.category === currentCategoryType;
                    const notExhausted = !exhaustedItems.includes(item.id);
                    const activeLimitOk = !maxActiveReached || !item.isActive;
                    return matchPrice && matchType && notExhausted && activeLimitOk;
                });

                if (pool.length === 0) break;

                const winner = pool[Math.floor(Math.random() * pool.length)];
                exhaustedItems.push(winner.id);
                pickedItems.push(winner);
                playersState[localPlayerNickname].items.push(winner);
                addToHistory(winner);
            }

            if (pickedItems.length > 0) {
                renderShowcaseContent(pickedItems[pickedItems.length - 1], false);
                updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
                
                if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                    partySocket.send(JSON.stringify({
                        type: 'sync',
                        nickname: myNickname,
                        state: playersState[localPlayerNickname]
                    }));
                }
            } else {
                alert('No more items available based on current limits/filters.');
            }
        });
    }

    function startRollAnimation(pool) {
        isRolling = true;
        rollButton.style.opacity = '0.5';
        rollButton.style.cursor = 'not-allowed';
        rollButton.querySelector('.roll-text').innerText = "CONJURING...";
        
        itemShowcase.classList.add('is-rolling');
        
        let rollInterval = setInterval(() => {
            const randomTempItem = pool[Math.floor(Math.random() * pool.length)];
            renderShowcaseContent(randomTempItem, true);
        }, 20);

        setTimeout(() => {
            clearInterval(rollInterval);
            itemShowcase.classList.remove('is-rolling');
            
            // Pick final winner
            const winner = pool[Math.floor(Math.random() * pool.length)];
            exhaustedItems.push(winner.id); 
            
            // Render winner
            renderShowcaseContent(winner, false);
            addToHistory(winner);
            
            // Update local state
            playersState[localPlayerNickname].items.push(winner);
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
            
            // Broadcast roll
            if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                partySocket.send(JSON.stringify({
                    type: 'item_roll',
                    nickname: myNickname,
                    item: winner
                }));
            }
            
            isRolling = false;
            rollButton.style.opacity = '1';
            rollButton.style.cursor = 'pointer';
            rollButton.querySelector('.roll-text').innerText = "ROLL ITEM";
            
        }, 250);
    }

    function renderShowcaseContent(item, isTemp) {
        const animationClass = isTemp ? '' : 'item-card ' + item.category;
        
        itemShowcase.innerHTML = `
            <div class="${animationClass}" style="${isTemp ? 'opacity: 0.3; width:100%; height:100%; display:flex; align-items:center; justify-content:center;' : ''}">
                ${!isTemp ? `
                    <div class="item-name">${item.name}</div>
                    <img src="${item.image}" alt="${item.name}" class="item-image">
                    <div class="item-meta">
                        <span class="item-price">${item.price}</span>
                        <span class="item-category">${item.category}</span>
                    </div>
                ` : `
                    <img src="${item.image}" alt="rolling" style="height:100px; filter:blur(4px);">
                `}
            </div>
        `;
    }

    function updatePlayerCard(nickname, isMe, state) {
        let side = isMe ? 'playersRight' : 'playersLeft';
        let container = document.getElementById(side);
        
        let cardId = 'player-card-' + nickname;
        let cardEl = document.getElementById(cardId);
        
        if (!cardEl) {
            if (!isMe) {
                const leftCount = document.getElementById('playersLeft').children.length;
                const rightCount = document.getElementById('playersRight').children.length;
                // Since right column has 'Me', put first 3 friends left, rest right
                if (leftCount < 3) side = 'playersLeft';
                else side = 'playersRight';
                container = document.getElementById(side);
            }
            
            cardEl = document.createElement('div');
            cardEl.id = cardId;
            cardEl.className = 'player-card' + (isMe ? ' is-me' : '');
            container.appendChild(cardEl);
        }
        
        const latestItem = state.items.length > 0 ? state.items[state.items.length - 1] : null;
        const heroImgSrc = latestItem ? latestItem.image : '';
        
        const totalCost = state.items.reduce((s, it) => s + (it.price || 0), 0);

        const generateGridHtml = (itemsArr, isMe, nick) => {
            let html = `<div class="inventory-grid">`;
            for (let i = 0; i < 15; i++) {
                if (i < itemsArr.length) {
                    const item = itemsArr[i];
                    const delBtn = isMe
                        ? `<button class="slot-delete-btn" data-idx="${i}" data-nick="${nick}" title="Remove">✕</button>`
                        : '';
                    html += `<div class="inventory-slot filled cat-${item.category.toLowerCase()}">
                                <span class="slot-number">${i+1}</span>
                                <img src="${item.image}" title="${item.name} — ${item.price}">
                                <div class="h-price" style="position:absolute;bottom:0;left:0;width:100%;background:rgba(0,0,0,0.8);text-align:center;font-size:0.55rem;font-family:var(--font-ui);padding:1px 0;font-weight:bold;color:var(--color-${item.category.toLowerCase()});">${item.price}</div>
                                ${delBtn}
                             </div>`;
                } else {
                    html += `<div class="inventory-slot"><span class="slot-number">${i+1}</span></div>`;
                }
            }
            html += `</div>`;
            return html;
        };

        let buildHtml = '';
        if (state.hasBuild && state.buildPath) {
            buildHtml = `<div class="player-build-grid">`;
            state.buildPath.forEach(step => {
                let mClass = step.cssClass.replace('t-', 'mini-t-');
                buildHtml += `<div class="mini-build-step ${mClass}">${step.name}</div>`;
            });
            buildHtml += `</div>`;
        }
        
        const costHtml = (state.hasBuild || state.items.length > 0) && totalCost > 0
            ? `<span class="p-build-cost">${totalCost.toLocaleString()} ⚡</span>` : '';

        cardEl.innerHTML = `
            <div class="player-header">
                <div class="player-avatar">
                    ${heroImgSrc ? `<img src="${heroImgSrc}">` : '<div style="font-family:var(--font-ui); color:#555;">?</div>'}
                </div>
                <div class="player-info-text">
                    <div class="p-nick">${nickname}</div>
                    <div class="p-status">
                        <div class="status-dot"></div> Connected
                        ${state.hasBuild ? '<span class="p-build-ready" style="margin-left:auto;">Build Ready</span>' : ''}
                        ${costHtml}
                    </div>
                </div>
            </div>
            <div class="player-inventory">
                ${generateGridHtml(state.items, isMe, nickname)}
            </div>
            ${buildHtml}
        `;

        // Wire delete buttons (only for local player)
        if (isMe) {
            cardEl.querySelectorAll('.slot-delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const idx = parseInt(btn.dataset.idx);
                    const nick = btn.dataset.nick;
                    if (!playersState[nick]) return;
                    const removed = playersState[nick].items.splice(idx, 1)[0];
                    if (removed) {
                        exhaustedItems = exhaustedItems.filter(id => id !== removed.id);
                        // Rebuild history
                        if (historyList) {
                            historyList.innerHTML = '';
                            playersState[nick].items.slice(-10).reverse().forEach(it => addToHistory(it));
                        }
                    }
                    updatePlayerCard(nick, true, playersState[nick]);
                    if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                        partySocket.send(JSON.stringify({ type: 'sync', nickname: myNickname, state: playersState[nick] }));
                    }
                });
            });
        }
    }

    function addToHistory(item) {
        if (!historyList) return;
        const historyItem = document.createElement('div');
        historyItem.className = 'history-item h-' + item.category.toLowerCase();
        historyItem.innerHTML = `
            <img src="${item.image}" alt="${item.name}" title="${item.name}">
            <div class="h-price">${item.price}</div>
        `;
        
        historyList.prepend(historyItem);
        
        if(historyList.children.length > 10) {
            historyList.removeChild(historyList.lastChild);
        }
    }

    // 4. Ability Randomizer Logic
    const generateBuildBtn = document.getElementById('generateBuildBtn');
    const abilityPathContainer = document.getElementById('abilityPath');

    if (generateBuildBtn) {
        generateBuildBtn.addEventListener('click', generateAbilityBuild);
    }

    function generateAbilityBuild() {
        generateBuildBtn.style.pointerEvents = 'none';
        generateBuildBtn.style.opacity = '0.5';

        // Try meta_rules first
        const heroId = heroSelect ? heroSelect.value : '';
        const diversity = tempToDiversity(currentTemperature);
        let path = tryGenerateFromMeta(heroId, diversity);

        if (!path) {
            // Fallback: pure random ability order
            let abilities = [
                { name: 'S1', stage: 0 }, { name: 'S2', stage: 0 },
                { name: 'S3', stage: 0 }, { name: 'Ult', stage: 0 }
            ];
            path = [];
            const labelMap = { 1:'UNL', 2:'T1', 3:'T2', 4:'T3' };
            const classMap = { 1:'t-unlock', 2:'t-tier1', 3:'t-tier2', 4:'t-tier3' };
            for (let i = 0; i < 16; i++) {
                let available = abilities.filter(a => a.stage < 4);
                let pick = available[Math.floor(Math.random() * available.length)];
                pick.stage++;
                path.push({ name: pick.name, label: labelMap[pick.stage], cssClass: classMap[pick.stage] });
            }
        }
        
        if (abilityPathContainer) {
            abilityPathContainer.innerHTML = '';
            path.forEach((step, index) => {
                const stepDiv = document.createElement('div');
                stepDiv.className = `timeline-step`;
                stepDiv.style.animation = `slideInRightDetail 0.3s forwards ${index * 0.04}s`;
                stepDiv.innerHTML = `
                    <div style="display:flex; align-items:center;">
                        <span class="step-index">${index + 1}.</span>
                        <span class="ability-name">${step.name}</span>
                    </div>
                    <span class="ability-tier ${step.cssClass}">${step.label}</span>
                `;
                abilityPathContainer.appendChild(stepDiv);
            });
        }
        
        playersState[localPlayerNickname].hasBuild = true;
        playersState[localPlayerNickname].buildPath = path;
        updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
        
        setTimeout(() => {
            generateBuildBtn.style.pointerEvents = 'auto';
            generateBuildBtn.style.opacity = '1';
            
            // Broadcast
            if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                partySocket.send(JSON.stringify({
                    type: 'ability_build',
                    nickname: myNickname,
                    path: path
                }));
            }
        }, 1000);
    }

    // 5. Party / Multiplayer Logic
    const createRoomBtn = document.getElementById('createRoomBtn');
    const joinRoomBtn = document.getElementById('joinRoomBtn');
    const leaveRoomBtn = document.getElementById('leaveRoomBtn');
    const nicknameInput = document.getElementById('nicknameInput');
    const roomCodeInput = document.getElementById('roomCodeInput');
    const roomInfo = document.getElementById('roomInfo');
    const partyControlsInputs = document.getElementById('partyControlsInputs');
    const currentRoomCodeEl = document.getElementById('currentRoomCode');
    const currentNicknameEl = document.getElementById('currentNickname');

    let partySocket = null;
    let myNickname = '';
    let myRoomCode = '';

    function generateRoomCode() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let result = '';
        for (let i = 0; i < 5; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }

    function connectToRoom(roomCode, nickname) {
        if (!nickname) {
            alert("Please enter a nickname first.");
            return;
        }
        
        localStorage.setItem('deadlockNick', nickname);
        
        if (localPlayerNickname !== nickname) {
            playersState[nickname] = playersState[localPlayerNickname] || { items: [], hasBuild: false };
            delete playersState[localPlayerNickname];
            
            const oldCard = document.getElementById('player-card-' + localPlayerNickname);
            if (oldCard) oldCard.remove();
            
            localPlayerNickname = nickname;
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
        }
        
        myNickname = nickname;
        myRoomCode = roomCode.toUpperCase();
        
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        partySocket = new WebSocket(`${protocol}${window.location.host}/ws/room/${myRoomCode}/`);
        
        partySocket.onopen = function(e) {
            partyControlsInputs.style.display = 'none';
            roomInfo.style.display = 'flex';
            currentRoomCodeEl.textContent = myRoomCode;
            currentNicknameEl.textContent = myNickname;
            
            partySocket.send(JSON.stringify({
                type: 'join',
                nickname: myNickname
            }));
            
            if (window.partyPingInterval) clearInterval(window.partyPingInterval);
            window.partyPingInterval = setInterval(() => {
                if (partySocket.readyState === WebSocket.OPEN) {
                    partySocket.send(JSON.stringify({ type: 'ping' }));
                }
            }, 3000);
        };
        
        partySocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            handlePartyMessage(data);
        };
        
        partySocket.onclose = function(e) {
            if (window.partyPingInterval) clearInterval(window.partyPingInterval);
            console.error('Party socket closed unexpectedly');
            leaveRoom();
        };
    }

    function leaveRoom() {
        if (window.partyPingInterval) clearInterval(window.partyPingInterval);
        if (partySocket) {
            partySocket.close();
            partySocket = null;
        }
        myRoomCode = '';
        partyControlsInputs.style.display = 'flex';
        roomInfo.style.display = 'none';
        window.location.href = '/';
    }

    createRoomBtn.addEventListener('click', () => {
        const nick = nicknameInput.value.trim();
        if (!nick) { alert("Please enter a nickname first."); return; }
        localStorage.setItem('deadlockNick', nick);
        window.location.href = '/room/' + generateRoomCode() + '/';
    });

    joinRoomBtn.addEventListener('click', () => {
        const code = roomCodeInput.value.trim();
        const nick = nicknameInput.value.trim();
        if (code.length < 3) { alert("Please enter a valid room code."); return; }
        if (!nick) { alert("Please enter a nickname first."); return; }
        localStorage.setItem('deadlockNick', nick);
        window.location.href = '/room/' + code.toUpperCase() + '/';
    });

    leaveRoomBtn.addEventListener('click', leaveRoom);
    
    // Auto-join logic if URL has room code
    const savedNick = localStorage.getItem('deadlockNick');
    if (savedNick) { nicknameInput.value = savedNick; }

    if (typeof INITIAL_ROOM_CODE !== 'undefined' && INITIAL_ROOM_CODE) {
        roomCodeInput.value = INITIAL_ROOM_CODE;
        if (savedNick) {
            connectToRoom(INITIAL_ROOM_CODE, savedNick);
        } else {
            nicknameInput.focus();
        }
    }

    function handlePartyMessage(data) {
        if (data.type === 'ping') return;
        if (data.nickname === myNickname) return; // Ignore my own messages
        
        if (data.type === 'leave') {
            if (playersState[data.nickname]) {
                delete playersState[data.nickname];
                const cardEl = document.getElementById('player-card-' + data.nickname);
                if (cardEl) cardEl.remove();
            }
            return;
        }

        if (data.type === 'reset') {
            playersState[data.nickname] = { items: [], hasBuild: false };
            updatePlayerCard(data.nickname, false, playersState[data.nickname]);
            return;
        }

        if (data.type === 'join') {
            // New player joined! Introduce myself and send my state
            if (typeof partySocket !== 'undefined' && partySocket && partySocket.readyState === WebSocket.OPEN) {
                partySocket.send(JSON.stringify({
                    type: 'sync',
                    nickname: myNickname,
                    state: playersState[localPlayerNickname]
                }));
            }
        }

        if (!playersState[data.nickname]) {
            playersState[data.nickname] = { items: [], hasBuild: false };
        }
        
        if (data.type === 'item_roll') {
            playersState[data.nickname].items.push(data.item);
        } else if (data.type === 'ability_build') {
            playersState[data.nickname].hasBuild = true;
            playersState[data.nickname].buildPath = data.path;
        } else if (data.type === 'sync') {
            playersState[data.nickname] = data.state;
        }
        
        updatePlayerCard(data.nickname, false, playersState[data.nickname]);
    }

    // ── Meta-aware build generator ──
    function weightedChoice(dict) {
        let total = 0;
        for (let k in dict) total += dict[k];
        let r = Math.random() * total;
        for (let k in dict) { r -= dict[k]; if (r <= 0) return k; }
        return Object.keys(dict)[0];
    }

    function tryGenerateFromMeta(heroId, diversity) {
        // If no hero chosen, pick random from available
        let targetId = heroId;
        if (!targetId || !metaRules[targetId]) {
            const ids = Object.keys(metaRules);
            if (!ids.length) return null;
            targetId = ids[Math.floor(Math.random() * ids.length)];
        }
        const heroData = metaRules[targetId];
        if (!heroData) return null;

        // Pick archetype weighted by popularity
        const archetypes = Object.entries(heroData);
        const archetypeWeights = {};
        archetypes.forEach(([id, d]) => { archetypeWeights[id] = d.popularity_weight || 1; });
        const archId = weightedChoice(archetypeWeights);
        const arch = heroData[archId];
        if (!arch || !arch.base_weights) return null;

        // Build item list using temperature
        const allItemsMap = {};
        itemsDatabase.forEach(it => { allItemsMap[it.id] = it; });

        let picked = [];
        let pickedIds = new Set();
        let spent = { Weapon: 0, Vitality: 0, Spirit: 0 };
        const SPIKE = 4800;

        for (let slot = 0; slot < 15; slot++) {
            let weights = {};
            for (let iid in arch.base_weights) {
                if (pickedIds.has(iid) || !allItemsMap[iid]) continue;
                let w = arch.base_weights[iid];
                // Temperature: low→ raise top items, high→ flatten weights
                const power = 2.0 - (diversity * 1.8); // META(0.1)→1.82  CHAOS(1.0)→0.2
                weights[iid] = Math.pow(Math.max(w, 0.1), power);
            }
            // Phase filter
            for (let iid in weights) {
                const it = allItemsMap[iid];
                if (!it) continue;
                if (slot < 4 && it.price >= 3000) weights[iid] *= 0.01;
                else if (slot < 9 && it.price >= 6200) weights[iid] *= 0.05;
                else if (slot >= 9 && it.price <= 800) weights[iid] *= 0.1;
                // Spike bonus
                const cat = it.category;
                if (cat && spent[cat] !== undefined) {
                    if (spent[cat] >= 2000 && spent[cat] < SPIKE) weights[iid] *= 3.0;
                    else if (spent[cat] >= SPIKE) weights[iid] *= 0.7;
                }
            }
            // Synergy rules
            if (arch.synergy_rules) {
                arch.synergy_rules.forEach(rule => {
                    const condMet = rule.antecedents.every(id => pickedIds.has(String(id)));
                    if (condMet) rule.consequents.forEach(cid => {
                        const s = String(cid);
                        if (weights[s]) weights[s] *= rule.lift * 1.5;
                    });
                });
            }
            if (!Object.keys(weights).length) break;
            const chosen = weightedChoice(weights);
            if (!chosen) break;
            pickedIds.add(chosen);
            const chosenItem = allItemsMap[chosen];
            if (!chosenItem) break;
            picked.push(chosenItem);
            if (spent[chosenItem.category] !== undefined) spent[chosenItem.category] += chosenItem.price;
        }

        // Also update player items with the generated build
        if (picked.length > 0) {
            exhaustedItems = [];
            playersState[localPlayerNickname].items = picked;
            picked.forEach(it => exhaustedItems.push(it.id));
            if (historyList) {
                historyList.innerHTML = '';
                picked.slice(-10).reverse().forEach(it => addToHistory(it));
            }
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
        }

        // Return ability path from sequences
        let path = [];
        if (arch.ability_sequences && arch.ability_sequences.length > 0) {
            // Temperature logic:
            // diversity is 0.1 to 1.0. 
            // We want low diversity to pick the first item (most popular).
            // High diversity picks randomly from the list.
            let idx = 0;
            if (diversity > 0.3) {
                // Determine max index based on diversity
                let maxIdx = Math.floor(diversity * arch.ability_sequences.length);
                if (maxIdx >= arch.ability_sequences.length) maxIdx = arch.ability_sequences.length - 1;
                idx = Math.floor(Math.random() * (maxIdx + 1));
            }
            path = arch.ability_sequences[idx].sequence;
        } else {
            // Fallback: pure random ability order
            const abilities = [
                { name: 'S1', stage: 0 }, { name: 'S2', stage: 0 },
                { name: 'S3', stage: 0 }, { name: 'Ult', stage: 0 }
            ];
            const lm = { 1:'UNL', 2:'T1', 3:'T2', 4:'T3' };
            const cm = { 1:'t-unlock', 2:'t-tier1', 3:'t-tier2', 4:'t-tier3' };
            for (let i = 0; i < 16; i++) {
                const av = abilities.filter(a => a.stage < 4);
                const pick = av[Math.floor(Math.random() * av.length)];
                pick.stage++;
                path.push({ name: pick.name, label: lm[pick.stage], cssClass: cm[pick.stage] });
            }
        }
        return path;
    }
});
