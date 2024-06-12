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

// Fetch the latest data from tbthermal table
$sql = "SELECT SuhuAC, RataSuhuAC, TCP, Microcontroller FROM tbthermal ORDER BY Id DESC LIMIT 1";
$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    $data = $result->fetch_assoc();
} else {
    $data = array(
        "SuhuAC" => 16, // default value
        "RataSuhuAC" => 0,
        "TCP" => 0,
        "Microcontroller" => 0
    );
}

echo json_encode($data);

$conn->close();
?>
