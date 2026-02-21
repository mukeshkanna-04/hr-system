// AGGRESSIVE REAL-TIME SYNC - Multi-Device Support
const API_BASE = window.location.origin;

// Force load from backend
async function loadFromBackend(force = false) {
    try {
        const res = await fetch(`${API_BASE}/api/data?t=${Date.now()}`); // Cache buster
        const data = await res.json();
        
        if (data.users) {
            const current = localStorage.getItem('hr_system_final_v5');
            const currentUser = current ? JSON.parse(current).currentUser : null;
            
            const systemData = {
                users: data.users,
                currentUser: currentUser,
                functionalGroups: ['D&L', 'Administration', 'Training', 'Rajbhasha', 'Pension', 'Time Office', 'Leave', 'Bills', 'DAK']
            };
            localStorage.setItem('hr_system_final_v5', JSON.stringify(systemData));
        }
        
        if (data.tasks) {
            localStorage.setItem('hr_tasks_v5', JSON.stringify(data.tasks));
        }
        
        console.log('✅ Synced:', data.users?.length || 0, 'users', data.tasks?.length || 0, 'tasks');
        
        // Force page refresh for user list
        if (force && typeof renderUserManagement === 'function') {
            renderUserManagement();
        }
        if (force && typeof renderDashboard === 'function') {
            renderDashboard();
        }
        
        return true;
    } catch (e) {
        console.error('Sync error:', e);
        return false;
    }
}

// Save to backend immediately
async function saveToBackend() {
    try {
        const systemData = localStorage.getItem('hr_system_final_v5');
        const tasksData = localStorage.getItem('hr_tasks_v5');
        
        if (!systemData || !tasksData) return;
        
        const system = JSON.parse(systemData);
        const tasks = JSON.parse(tasksData);
        
        await fetch(`${API_BASE}/api/data`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                users: system.users || [],
                tasks: tasks || []
            })
        });
        
        console.log('💾 Saved to MongoDB');
    } catch (e) {
        console.error('Save error:', e);
    }
}

// Initial load
window.addEventListener('DOMContentLoaded', async () => {
    console.log('🔄 Loading from MongoDB...');
    await loadFromBackend(true);
});

// CRITICAL: Auto-refresh every 2 seconds (faster!)
setInterval(() => loadFromBackend(true), 2000);

// Save every 1 second
setInterval(saveToBackend, 1000);

// Intercept localStorage changes
const originalSetItem = localStorage.setItem;
localStorage.setItem = function(key, value) {
    originalSetItem.call(localStorage, key, value);
    if (key === 'hr_system_final_v5' || key === 'hr_tasks_v5') {
        setTimeout(saveToBackend, 100); // Immediate save!
    }
};

// Add manual refresh button
window.forceSync = async function() {
    console.log('🔄 Manual sync...');
    await saveToBackend();
    await loadFromBackend(true);
    alert('✅ Synced! New users should appear now.');
};

console.log('✅ REAL-TIME SYNC ACTIVE');
console.log('⚡ Auto-refresh: Every 2 seconds');
console.log('💾 Auto-save: Every 1 second');
console.log('🔄 Type forceSync() in console to manually sync');
