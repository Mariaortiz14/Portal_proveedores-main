
var data = {
    value: 0,
    max: 100,
    label: "Progress"
};

var config = {
    type: 'doughnut',
    data: {
        datasets: [{
            data: [data.value, data.max - data.value],
            backgroundColor: ['rgba(253,13,19, 0.8)', 'rgba(0, 0, 0, 0.1)'],
            borderWidth: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        cutoutPercentage: 85,
        rotation: -90,
        circumference: 180,
        tooltips: {
            enabled: false
        },
        legend: {
            display: false
        },
        animation: {
            animateRotate: true,
            animateScale: false
        },
        title: {
            display: true,
            text: data.label,
            fontSize: 16
        }
    }
};


var chartCtx = document.getElementById('gaugeChart').getContext('2d');
var gaugeChart = new Chart(chartCtx, config);