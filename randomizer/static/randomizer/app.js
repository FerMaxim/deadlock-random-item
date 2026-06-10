document.addEventListener('DOMContentLoaded', () => {
    let itemsDatabase = [];
    let currentCategoryPrice = 'all'; // Default
    let currentCategoryType = 'all'; // 'all', 'Weapon', 'Vitality', 'Spirit'
    let isRolling = false;
    let exhaustedItems = []; // Global history to prevent ANY repeats

    const rollButton = document.getElementById('rollButton');
    const priceButtons = document.querySelectorAll('.price-group .btn');
    const typeButtons = document.querySelectorAll('.type-group .btn');
    const itemShowcase = document.getElementById('itemShowcase');
    const newGameBtn = document.getElementById('newGameBtn');
    const historyList = document.getElementById('historyList');

    // Player States
    let playersState = {};
    let localPlayerNickname = 'Me';
    
    // Initialize Local Player
    playersState[localPlayerNickname] = { items: [], hasBuild: false };
    
    // 1. Fetch data
    fetch('/static/randomizer/data.json')
        .then(response => response.json())
        .then(data => {
            itemsDatabase = data;
            console.log('Items loaded:', itemsDatabase.length);
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
        })
        .catch(err => {
            console.error('Failed to load items:', err);
            itemShowcase.innerHTML = `<div class="idle-state"><p style="color:red">Error loading item database.</p></div>`;
        });

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

    // New Game Reset Logic
    if (newGameBtn) {
        newGameBtn.addEventListener('click', () => {
            if (isRolling) return;
            
            // Clear history and exhausted items
            exhaustedItems = [];
            if (historyList) historyList.innerHTML = '';
            playersState[localPlayerNickname] = { items: [], hasBuild: false };
            updatePlayerCard(localPlayerNickname, true, playersState[localPlayerNickname]);
            
            // Reset showcase
            itemShowcase.innerHTML = `
                <div class="idle-state">
                    <div class="scanner-line"></div>
                    <div class="occult-rune"></div>
                    <p>AWAITING INPUT...</p>
                </div>
            `;
            
            // Reset build timeline
            const abilityPathContainer = document.getElementById('abilityPath');
            if(abilityPathContainer) abilityPathContainer.innerHTML = '';
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
        
        const generateGridHtml = (itemsArr) => {
            let html = `<div class="inventory-grid">`;
            for (let i = 0; i < 15; i++) {
                if (i < itemsArr.length) {
                    const item = itemsArr[i];
                    html += `<div class="inventory-slot filled cat-${item.category.toLowerCase()}">
                                <span class="slot-number">${i+1}</span>
                                <img src="${item.image}" title="${item.name}">
                                <div class="h-price" style="position: absolute; bottom: 0; left: 0; width: 100%; background: rgba(0,0,0,0.8); text-align: center; font-size: 0.55rem; font-family: var(--font-ui); padding: 1px 0; font-weight: bold; color: var(--color-${item.category.toLowerCase()});">${item.price}</div>
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
                    </div>
                </div>
            </div>
            <div class="player-inventory">
                ${generateGridHtml(state.items)}
            </div>
            ${buildHtml}
        `;
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
        
        let abilities = [
            { name: 'S1', stage: 0 },
            { name: 'S2', stage: 0 },
            { name: 'S3', stage: 0 },
            { name: 'Ult', stage: 0 }
        ];
        
        let path = [];
        let labelMap = { 1: 'UNL', 2: 'T1', 3: 'T2', 4: 'T3' };
        let classMap = { 1: 't-unlock', 2: 't-tier1', 3: 't-tier2', 4: 't-tier3' };
        
        for (let i = 0; i < 16; i++) {
            let available = abilities.filter(a => a.stage < 4);
            let pick = available[Math.floor(Math.random() * available.length)];
            pick.stage++;
            
            path.push({
                name: pick.name,
                label: labelMap[pick.stage],
                cssClass: classMap[pick.stage]
            });
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
        if (data.nickname === myNickname) return; // Ignore my own messages
        
        if (data.type === 'leave') {
            if (playersState[data.nickname]) {
                delete playersState[data.nickname];
                const cardEl = document.getElementById('player-card-' + data.nickname);
                if (cardEl) cardEl.remove();
            }
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
});
