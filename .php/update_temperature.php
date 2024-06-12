<?php
$servername = "localhost";
$username = "root"; // Adjust this if your MySQL username is different
$password = ""; // Adjust this if your MySQL password is different
$dbname = "pbl1";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $suhuAC = $_POST["SuhuAC"];
    $sql = "UPDATE tbthermal SET SuhuAC = $suhuAC ORDER BY Id DESC LIMIT 1";

    if ($conn->query($sql) === TRUE) {
        echo "Temperature updated successfully";
    } else {
        echo "Error updating temperature: " . $conn->error;
    }
}

$conn->close();
?>
