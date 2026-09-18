const dateInput = document.getElementById('date');
if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
}

if (window.location.search.includes('cleared=true')) {
    document.getElementById('clear-message').style.display = 'block';
    
    setTimeout(() => {
        document.getElementById('clear-message').style.display = 'none';
        window.history.replaceState({}, document.title, '/');
    }, 5000);
}

const clearBtn = document.querySelector('.btn-danger');
let confirmed = false;

clearBtn.addEventListener('click', function(e) {
    if (!confirmed) {
        e.preventDefault();
        clearBtn.textContent = 'Press again to confirm';
        clearBtn.style.backgroundColor = '#dc2626';
        confirmed = true;

        setTimeout(() => {
            clearBtn.textContent = 'Clear Database';
            clearBtn.style.backgroundColor = '';
            confirmed = false;
        }, 3000);
    }
});

const archive = document.querySelectorAll('.archive');
archive.forEach((btn) => {
    btn.addEventListener('click', () => {
        const row = btn.closest('tr');
        row.classList.toggle("archived")
    })
})
// Edit button — show edit row, hide display row
document.querySelectorAll('.edit').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.dataset.id;
        document.getElementById(`row-${id}`).style.display = 'none';
        document.getElementById(`edit-row-${id}`).style.display = '';
    });
});

// Cancel button — show display row, hide edit row
document.querySelectorAll('.cancel-edit').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.dataset.id;
        document.getElementById(`row-${id}`).style.display = '';
        document.getElementById(`edit-row-${id}`).style.display = 'none';
    });
});

// Confirm button — send update to Flask via fetch
document.querySelectorAll('.confirm-edit').forEach(button => {
    button.addEventListener('click', function() {
        const id = this.dataset.id;
        const editRow = document.getElementById(`edit-row-${id}`);

        const role = editRow.querySelector('.edit-role').value;
        const status = editRow.querySelector('.edit-status').value;
        const date = editRow.querySelector('.edit-date').value;
        const notes = editRow.querySelector('.edit-notes').value;

        fetch('/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, role, status, date_applied: date, notes })
        }).then(() => {
            window.location.reload();
        });
    });
});
