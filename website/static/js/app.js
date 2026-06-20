document.addEventListener("DOMContentLoaded", () => {
    // --- State ---
    let myNickname = "Player";
    let roomCode = INITIAL_ROOM_CODE;
    let ws = null;
    let selectedHeroId = null;
    
    let playersState = {}; // { nick: { hero: 0, items: [], abilities: [], cost: 0 } }
    
    // --- Elements ---
    const heroGrid = document.getElementById("heroGrid");
    const tempSlider = document.getElementById("tempSlider");
    const tempLabel = document.getElementById("tempLabel");
    const generateBuildBtn = document.getElementById("generateBuildBtn");
    const abilityPath = document.getElementById("abilityPath");
    
    const playersLeft = document.getElementById("playersLeft");
    const playersRight = document.getElementById("playersRight");
    
    // --- Initialization ---
    initHeroGrid();
    setupTemperature();
    setupParty();
    
    if (roomCode) {
        connectWebSocket();
    } else {
        // Solo mode card
        playersState[myNickname] = { hero: 0, items: [], abilities: [], cost: 0 };
        renderPlayers();
    }
    
    function initHeroGrid() {
        const activeHeroes = ['random', 1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 25, 27, 31, 35, 50, 52, 58, 60, 63, 64, 65, 66, 67, 69, 72, 76, 77, 79, 80, 81];
        activeHeroes.forEach(id => {
            const div = document.createElement("div");
            div.className = "hero-avatar";
            if (id === 'random') {
                div.innerHTML = `<div style="width:100%; height:100%; display:flex; justify-content:center; align-items:center; font-size:24px; font-weight:bold;">?</div>`;
            } else {
                div.innerHTML = `<img src="/static/images/heroes/${id}.png" alt="Hero ${id}" onerror="this.style.display='none'">`;
            }
            div.onclick = () => {
                document.querySelectorAll(".hero-avatar").forEach(el => el.classList.remove("selected"));
                div.classList.add("selected");
                selectedHeroId = id;
            };
            heroGrid.appendChild(div);
        });
    }

    function setupTemperature() {
        const labels = {
            1: { text: "META", class: "temp-meta", color: "#3498db" },
            2: { text: "STABLE", class: "temp-stable", color: "#5ebd40" },
            3: { text: "MIXED", class: "temp-mixed", color: "#c3a156" },
            4: { text: "WILD", class: "temp-wild", color: "#d3783a" },
            5: { text: "CHAOS", class: "temp-chaos", color: "#e74c3c" }
        };
        tempSlider.addEventListener("input", (e) => {
            const val = e.target.value;
            tempLabel.textContent = labels[val].text;
            tempLabel.style.color = labels[val].color;
            tempLabel.style.boxShadow = `0 0 10px ${labels[val].color}`;
        });
    }
    
    function setupParty() {
        document.getElementById("createRoomBtn").addEventListener("click", () => {
            let nick = document.getElementById("nicknameInput").value.trim();
            if(!nick) nick = "Player_" + Math.floor(1000 + Math.random() * 9000);
            sessionStorage.setItem("myNickname", nick);
            const code = Math.random().toString(36).substring(2, 7).toUpperCase();
            window.location.href = `/room/${code}/`;
        });
        document.getElementById("joinRoomBtn").addEventListener("click", () => {
            let nick = document.getElementById("nicknameInput").value.trim();
            if(!nick) nick = "Player_" + Math.floor(1000 + Math.random() * 9000);
            sessionStorage.setItem("myNickname", nick);
            const code = document.getElementById("roomCodeInput").value.toUpperCase();
            if(code) window.location.href = `/room/${code}/`;
        });
        document.getElementById("leaveRoomBtn").addEventListener("click", () => {
            sessionStorage.removeItem("myState");
            window.location.href = `/`;
        });
    }
    
    // --- Game Logic ---
    generateBuildBtn.addEventListener("click", async () => {
        const tempMap = {1: 0.1, 2: 1.0, 3: 2.0, 4: 5.0, 5: 15.0};
        const temp = tempMap[tempSlider.value];
        
        generateBuildBtn.style.opacity = "0.5";
        
        try {
            const res = await fetch('/api/generate_build/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ hero_id: selectedHeroId, temperature: temp })
            });
            const data = await res.json();
            
            if (data.success) {
                playersState[myNickname] = {
                    hero: data.hero_id,
                    items: data.items,
                    abilities: data.abilities,
                    cost: data.cost,
                    archetype: data.archetype
                };
                
                sessionStorage.setItem("myState", JSON.stringify(playersState[myNickname]));
                
                renderPlayers();
                renderAbilityTimeline(data.abilities);
                addHistory(data.items);
                
                if (ws) {
                    ws.send(JSON.stringify({
                        type: 'update',
                        nick: myNickname,
                        state: playersState[myNickname]
                    }));
                }
            } else {
                alert(data.error);
            }
        } catch(e) { console.error(e); }
        
        generateBuildBtn.style.opacity = "1";
    });
    
    function renderAbilityTimeline(abilities) {
        abilityPath.innerHTML = "";
        abilities.forEach((ab, index) => {
            setTimeout(() => {
                const step = document.createElement("div");
                step.className = "timeline-step";
                
                let badgeClass = "t-unl";
                let badgeText = "UNL";
                if (ab.level_reached === 2) { badgeClass = "t-tier1"; badgeText = "T1"; }
                if (ab.level_reached === 3) { badgeClass = "t-tier2"; badgeText = "T2"; }
                if (ab.level_reached === 4) { badgeClass = "t-tier3"; badgeText = "T3"; }
                
                step.innerHTML = `
                    <span class="step-num">${index+1}.</span> <span class="step-name">${ab.short_name}</span>
                    <span class="step-badge ${badgeClass}">${badgeText}</span>
                `;
                abilityPath.appendChild(step);
            }, index * 100); // cascade animation
        });
    }

    function renderPlayers() {
        playersLeft.innerHTML = "";
        playersRight.innerHTML = "";
        
        const nicks = Object.keys(playersState);
        
        // Ensure "Me" is on the right
        const others = nicks.filter(n => n !== myNickname);
        let leftTurn = true;
        
        others.forEach(nick => {
            const card = buildPlayerCard(nick, playersState[nick], false);
            if (leftTurn) { playersLeft.appendChild(card); }
            else { playersRight.appendChild(card); }
            leftTurn = !leftTurn;
        });
        
        // Add Me
        if (playersState[myNickname]) {
            playersRight.prepend(buildPlayerCard(myNickname, playersState[myNickname], true));
        }
    }
    
    function buildPlayerCard(nick, state, isMe) {
        const div = document.createElement("div");
        div.className = "player-card panel-glass";
        
        let gridHtml = `<div class="inventory-grid">`;
        // 24 slots (6x4 grid)
        for(let i=0; i<24; i++) {
            const item = state.items[i];
            if (item) {
                gridHtml += `
                    <div class="inv-slot filled cat-${item.slot}">
                        <span class="slot-number">${i+1}</span>
                        <img src="/static/images/items/${item.slot}/${encodeURIComponent(item.name)}.png" alt="${item.name}" onerror="this.style.display='none'">
                        <div class="item-cost">${item.cost}</div>
                        ${isMe ? `<button class="remove-item-btn" data-index="${i}">×</button>` : ''}
                    </div>
                `;
            } else {
                gridHtml += `<div class="inv-slot"><span class="slot-number">${i+1}</span></div>`;
            }
        }
        gridHtml += `</div>`;
        
        let abilitiesHtml = "";
        if (state.abilities && state.abilities.length > 0) {
            abilitiesHtml += `<div class="player-abilities-grid">`;
            state.abilities.forEach(ab => {
                let badgeClass = "t-unl";
                if (ab.level_reached === 2) badgeClass = "t-tier1";
                if (ab.level_reached === 3) badgeClass = "t-tier2";
                if (ab.level_reached === 4) badgeClass = "t-tier3";
                
                abilitiesHtml += `<div class="player-ability-slot ${badgeClass}">${ab.short_name}</div>`;
            });
            abilitiesHtml += `</div>`;
        }
        
        const displayNick = isMe ? "Me" : nick;
        
        div.innerHTML = `
            <div class="player-header">
                <div class="player-avatar">${state.hero ? `<img src="/static/images/heroes/${state.hero}.png" alt="Hero ${state.hero}" onerror="this.style.display='none'">` : '?'}</div>
                <div>
                    <div class="player-nick">${displayNick} <div class="status-dot"></div></div>
                    <span class="player-cost">Total: ⚡${state.cost} <span style="margin-left:10px; color:#888;">| ${state.archetype || ''}</span></span>
                </div>
            </div>
            ${gridHtml}
            ${abilitiesHtml}
        `;
        return div;
    }
    
    function addHistory(items) {
        const h = document.getElementById("historyList");
        h.innerHTML = ""; // Clear for new build
        items.forEach(item => {
            const div = document.createElement("div");
            div.className = `history-item cat-${item.slot}`;
            div.innerHTML = `
                <img src="/static/images/items/${item.slot}/${encodeURIComponent(item.name)}.png" alt="${item.name}" onerror="this.style.display='none'">
                <div class="hist-cost">${item.cost}</div>
            `;
            h.appendChild(div);
        });
    }
    
    // Reset Button
    const resetBtn = document.querySelector(".my-history button");
    if (resetBtn) {
        resetBtn.addEventListener("click", () => {
            document.getElementById("historyList").innerHTML = "";
            abilityPath.innerHTML = '<div style="color: #666; font-family: var(--font-body); font-style: italic;">AWAITING INPUT...</div>';
            playersState[myNickname] = { hero: 0, items: [], abilities: [], cost: 0, archetype: "" };
            sessionStorage.removeItem("myState");
            renderPlayers();
            if (ws) {
                ws.send(JSON.stringify({ type: 'update', nick: myNickname, state: playersState[myNickname] }));
            }
        });
    }
    
    // Remove Item Listener
    document.body.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-item-btn')) {
            const index = parseInt(e.target.getAttribute('data-index'));
            const state = playersState[myNickname];
            if (state && state.items && state.items.length > index) {
                state.cost -= state.items[index].cost;
                state.items.splice(index, 1);
                sessionStorage.setItem("myState", JSON.stringify(state));
                renderPlayers();
                if (ws) {
                    ws.send(JSON.stringify({ type: 'update', nick: myNickname, state: state }));
                }
            }
        }
    });
    
    // --- WebSocket ---
    function connectWebSocket() {
        myNickname = sessionStorage.getItem("myNickname");
        if (!myNickname) {
            const params = new URLSearchParams(window.location.search);
            myNickname = params.get('nick') || ("Player_" + Math.floor(1000 + Math.random() * 9000));
            sessionStorage.setItem("myNickname", myNickname);
        }
        
        document.getElementById("partyControlsInputs").style.display = "none";
        document.getElementById("roomInfo").style.display = "flex";
        document.getElementById("currentRoomCode").textContent = roomCode;
        document.getElementById("currentNickname").textContent = myNickname;
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/room/${roomCode}/`);
        
        ws.onopen = () => {
            let savedState = sessionStorage.getItem("myState");
            if (savedState) {
                playersState[myNickname] = JSON.parse(savedState);
            } else {
                playersState[myNickname] = { hero: 0, items: [], abilities: [], cost: 0 };
            }
            
            ws.send(JSON.stringify({ type: 'join', nick: myNickname, state: playersState[myNickname] }));
            renderPlayers();
        };
        
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'join' || data.type === 'update') {
                playersState[data.nick] = data.state;
                renderPlayers();
                if (data.type === 'join') {
                    // Always respond to new joins with our current state so they can see us
                    ws.send(JSON.stringify({ type: 'update', nick: myNickname, state: playersState[myNickname] }));
                }
            }
        };
    }
});
