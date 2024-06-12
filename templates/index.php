<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CCTV Thermal HVAC Monitoring</title>
    <link
      rel="stylesheet"
      href="{{ url_for('static', filename='style.css') }}"
    />
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
      $(document).ready(function () {
        function fetchData() {
          $.getJSON("fetch_data.php", function (data) {
            $("#AirConditionerTemp").text(data.SuhuAC + "°C");
            $("#CCTVTemp").text(data.RataSuhuAC + "°C");
            $("#tcp-toggle").prop("checked", data.TCP == 1);
            $("#microcontroller-toggle").prop("checked", data.Microcontroller == 1);
          });
        }

        fetchData(); // Initial data fetch
        setInterval(fetchData, 5000); // Update every 5 seconds

        $(".up-button").click(function () {
          adjustTemperature(1);
        });

        $(".down-button").click(function () {
          adjustTemperature(-1);
        });

        function adjustTemperature(change) {
          let currentTemp = parseInt($("#AirConditionerTemp").text());
          let newTemp = currentTemp + change;
          if (newTemp >= 16 && newTemp <= 30) {
            $("#AirConditionerTemp").text(newTemp + "°C");
            updateDatabase(newTemp);
          } else {
            alert("Temperature must be between 16°C and 30°C.");
          }
        }

        function updateDatabase(temp) {
          $.post("update_temperature.php", { SuhuAC: temp }, function (response) {
            console.log(response);
          });
        }

        function updateDateTime() {
          const now = new Date();
          const formattedDateTime = now.toLocaleString("en-US", {
            weekday: "long",
            day: "numeric",
            month: "long",
            year: "numeric",
            hour: "numeric",
            minute: "numeric",
            second: "numeric",
            hour12: true,
          });
          $("#datetime").text(formattedDateTime);
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
        <img src="video_feed" width="1000" />
      </div>
      <div class="row">
        <div class="card">
          <h2>TCP</h2>
          <label class="toggle-switch">
            <input type="checkbox" id="tcp-toggle" />
            <span class="slider"></span>
          </label>
        </div>
        <div class="card">
          <h2>Air Conditioner Temperature</h2>
          <div id="air-conditioner" class="temperature-control">
            <button class="control-button up-button">&#9650;</button>
            <p><span id="AirConditionerTemp">16°C</span></p>
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
            <input type="checkbox" id="microcontroller-toggle" />
            <span class="slider"></span>
          </label>
        </div>
      </div>
    </main>
  </body>
</html>
