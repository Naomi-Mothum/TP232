let students = [];
let analysisResults = null;
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
    fetchStudents();
});

async function fetchStudents() {
    try {
        const response = await fetch('/api/students');
        students = await response.json();
        renderTable();
    } catch (error) {
        console.error('Erreur lors de la récupération des étudiants:', error);
    }
}

function renderTable() {
    const tbody = document.querySelector('#student-table tbody');
    tbody.innerHTML = students.map(s => `
        <tr>
            <td>#${s.id}</td>
            <td>${s.age}</td>
            <td>${s.gender === 'M' ? 'Masc' : 'Fém'}</td>
            <td>${s.study_time}h</td>
            <td>${s.absences}</td>
            <td>${s.prev_grade}</td>
            <td><span class="badge ${s.final_grade >= 10 ? 'badge-pass' : 'badge-fail'}">${s.final_grade}</span></td>
            <td><button class="btn btn-secondary" style="padding: 2px 8px; font-size: 0.7rem;" onclick="deleteStudent(${s.id})">Supprimer</button></td>
        </tr>
    `).join('');
}

async function handleFormSubmit(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    
    // Convert types
    data.age = parseInt(data.age);
    data.study_time = parseInt(data.study_time);
    data.absences = parseInt(data.absences);
    data.prev_grade = parseFloat(data.prev_grade);
    data.final_grade = parseFloat(data.final_grade);

    try {
        const response = await fetch('/api/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            event.target.reset();
            fetchStudents();
        }
    } catch (error) {
        alert('Erreur lors de l\'enregistrement des données');
    }
}

async function deleteStudent(id) {
    if (!confirm('Êtes-vous sûr ?')) return;
    try {
        await fetch(`/api/students/${id}`, { method: 'DELETE' });
        fetchStudents();
    } catch (error) {
        alert('Erreur lors de la suppression');
    }
}

async function handleCsvUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/upload-csv', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        alert(result.message);
        fetchStudents();
    } catch (error) {
        alert('Erreur lors de l\'importation du CSV');
    }
}

async function triggerAnalysis() {
    try {
        const response = await fetch('/api/analysis');
        if (!response.ok) {
            const err = await response.json();
            alert(err.detail);
            return;
        }
        analysisResults = await response.json();
        renderAnalysisSummary();
        renderCharts();
    } catch (error) {
        alert('Erreur lors de l\'analyse');
    }
}

function renderAnalysisSummary() {
    const summaryDiv = document.getElementById('analysis-summary');
    const { multiple_regression, pass_fail_prediction } = analysisResults;
    
    summaryDiv.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; color: var(--text-muted);">R² de la régression multiple</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--primary);">${multiple_regression.r2.toFixed(3)}</div>
        </div>
        <div style="margin-bottom: 1rem;">
            <div style="font-size: 0.8rem; color: var(--text-muted);">Précision (Réussite/Échec)</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: var(--secondary);">${(pass_fail_prediction.accuracy * 100).toFixed(1)}%</div>
        </div>
        <p style="font-size: 0.85rem; color: var(--text-muted);">
            Selon les données actuelles, le facteur <b>temps_étude</b> a l'impact positif le plus fort sur les notes.
        </p>
    `;
}

function renderCharts() {
    renderRegressionChart();
    renderClusterChart();
    renderPcaChart();
    renderCoeffChart();
}

function destroyChart(id) {
    if (charts[id]) {
        charts[id].destroy();
    }
}

function renderRegressionChart() {
    destroyChart('regression');
    const ctx = document.getElementById('regressionChart').getContext('2d');
    
    // Scatter data
    const scatterData = students.map(s => ({ x: s.study_time, y: s.final_grade }));
    // Line data
    const lineData = analysisResults.simple_regression.line;

    charts['regression'] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Étudiants',
                data: scatterData,
                backgroundColor: 'rgba(99, 102, 241, 0.5)',
            }, {
                label: 'Ligne de régression',
                data: lineData,
                type: 'line',
                borderColor: '#ec4899',
                borderWidth: 2,
                pointRadius: 0,
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Temps d\'étude (h)', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { title: { display: true, text: 'Note Finale', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });
}

function renderClusterChart() {
    destroyChart('cluster');
    const ctx = document.getElementById('clusterChart').getContext('2d');
    
    // Group analysis markers by cluster
    const clusterMap = {};
    analysisResults.clusters.forEach(c => {
        const student = students.find(s => s.id === c.id);
        if (!student) return;
        if (!clusterMap[c.cluster]) clusterMap[c.cluster] = [];
        clusterMap[c.cluster].push({ x: student.study_time, y: student.absences });
    });

    const colors = ['#6366f1', '#ec4899', '#8b5cf6'];
    const datasets = Object.keys(clusterMap).map((k, i) => ({
        label: `Profil ${parseInt(k) + 1}`,
        data: clusterMap[k],
        backgroundColor: colors[i % colors.length]
    }));

    charts['cluster'] = new Chart(ctx, {
        type: 'scatter',
        data: { datasets },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Temps d\'étude', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { title: { display: true, text: 'Absences', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });
}

function renderPcaChart() {
    destroyChart('pca');
    const ctx = document.getElementById('pcaChart').getContext('2d');
    
    charts['pca'] = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Projection PCA',
                data: analysisResults.pca_data,
                backgroundColor: 'rgba(139, 92, 246, 0.6)',
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'PC1', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { title: { display: true, text: 'PC2', color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
            },
            plugins: { legend: { labels: { color: '#f8fafc' } } }
        }
    });
}

function renderCoeffChart() {
    destroyChart('coeff');
    const ctx = document.getElementById('coeffChart').getContext('2d');
    
    const coeffs = analysisResults.multiple_regression.coefficients;
    const labels = Object.keys(coeffs).map(l => {
        const trans = {
            'age': 'Âge',
            'gender_numeric': 'Genre',
            'study_time': 'Étude',
            'absences': 'Absences',
            'prev_grade': 'Note Préc.'
        };
        return trans[l] || l;
    });
    const values = Object.values(coeffs);

    charts['coeff'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Facteur d\'impact',
                data: values,
                backgroundColor: values.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.6)' : 'rgba(239, 68, 68, 0.6)'),
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, border: { color: 'rgba(255,255,255,0.1)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { display: false } }
            },
            plugins: { legend: { display: false } }
        }
    });
}
