const API = window.location.origin;
async function load() {
    try {
        const r = await fetch(`${API}/api/data?t=${Date.now()}`);
        const d = await r.json();
        if (d.users) {
            const c = localStorage.getItem('hr_system_final_v5');
            const u = c ? JSON.parse(c).currentUser : null;
            localStorage.setItem('hr_system_final_v5', JSON.stringify({
                users: d.users, currentUser: u,
                functionalGroups: ['D&L','Administration','Training','Rajbhasha','Pension','Time Office','Leave','Bills','DAK']
            }));
        }
        if (d.tasks) localStorage.setItem('hr_tasks_v5', JSON.stringify(d.tasks));
        console.log('✅ Synced:', d.users?.length || 0, 'users');
        if (typeof renderUserManagement === 'function') renderUserManagement();
    } catch(e) { console.error('Sync error:', e); }
}
async function save() {
    try {
        const s = localStorage.getItem('hr_system_final_v5');
        const t = localStorage.getItem('hr_tasks_v5');
        if (s && t) {
            const sys = JSON.parse(s);
            const tsk = JSON.parse(t);
            await fetch(`${API}/api/data`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({users: sys.users || [], tasks: tsk || []})
            });
            console.log('💾 Saved');
        }
    } catch(e) {}
}
window.addEventListener('DOMContentLoaded', () => load());
setInterval(load, 2000);
setInterval(save, 1000);
const orig = localStorage.setItem;
localStorage.setItem = function(k,v) {
    orig.call(localStorage,k,v);
    if (k === 'hr_system_final_v5' || k === 'hr_tasks_v5') setTimeout(save, 100);
};
console.log('✅ MongoDB sync active');
