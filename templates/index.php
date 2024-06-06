<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CCTV Thermal HVAC Monitoring</title>
  <link rel="stylesheet" href="style.css">
  <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
  <script>
    $(document).ready(function() {
      function updateData() {
        $.getJSON('fetch_data.php', function(data) {
          $('#AirConditionerTemp').text(data.air_conditioner_temp);
          $('#CCTVTemp').text(data.cctv_avg_temp);
          $('#tcp-toggle').prop('checked', data.tcp_status);
          $('#microcontroller-toggle').prop('checked', data.microcontroller_status);
        });
      }
      setInterval(updateData, 5000); // Fetch data every 5 seconds
      updateData(); // Initial fetch

      $('#tcp-toggle').change(function() {
        const status = $(this).is(':checked');
        $.post('update_status.php', { tcp_status: status });
      });

      $('#microcontroller-toggle').change(function() {
        const status = $(this).is(':checked');
        $.post('update_status.php', { microcontroller_status: status });
      });

      $('.up-button').click(function() {
        adjustTemperature(1);
      });

      $('.down-button').click(function() {
        adjustTemperature(-1);
      });

      function adjustTemperature(change) {
        let currentTemp = parseInt($('#AirConditionerTemp').text());
        let newTemp = currentTemp + change;
        $.post('update_temp.php', { air_conditioner_temp: newTemp }, function(response) {
          if (response.success) {
            $('#AirConditionerTemp').text(newTemp + '°C');
          } else {
            alert('Failed to update temperature');
          }
        });
      }

      function updateDateTime() {
        const now = new Date();
        const formattedDateTime = now.toLocaleString('en-US', {
          weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
          hour: 'numeric', minute: 'numeric', second: 'numeric', hour12: true
        });
        $('#datetime').text(formattedDateTime);
      }
      setInterval(updateDateTime, 1000);
    });
  </script>
</head>
<body>
  <header>
    <h1>Monitoring CCTV Thermal HVAC</h1>
    <p id="datetime"></p>
  </header>

  <main class="main">
    <div class="video-container">
      <img src="raihan2.jpg" width="1200">
    </div>
    <div class="row">
      <div class="card">
        <h2>TCP</h2>
        <label class="toggle-switch">
          <input type="checkbox" id="tcp-toggle">
          <span class="slider"></span>
        </label>
      </div>
      <div class="card">
        <h2>Air Conditioner Temperature</h2>
        <div id="air-conditioner" class="temperature-control">
          <button class="control-button up-button">&#9650;</button>
          <p><span id="AirConditionerTemp">0</span>°C</p>
          <button class="control-button down-button">&#9660;</button>
        </div>
      </div>
      <div class="card">
        <h2>CCTV Average Temperature</h2>
        <p><span id="CCTVTemp">0</span>°C</p>
      </div>
      <div class="card">
        <h2>Microcontroller</h2>
        <label class="toggle-switch">
          <input type="checkbox" id="microcontroller-toggle">
          <span class="slider"></span>
        </label>
      </div>
    </div>
  </main>
</body>
</html>
