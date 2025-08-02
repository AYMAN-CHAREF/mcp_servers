<?php

$filename = '../users.json';

function readUsers($filename) {
    if (!file_exists($filename)) return [];
    return json_decode(file_get_contents($filename), true);
}

function saveUsers($filename, $users) {
    file_put_contents($filename, json_encode($users, JSON_PRETTY_PRINT));
}

$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    echo json_encode(readUsers($filename));
    exit;
}

if ($method === 'POST') {
    $data = json_decode(file_get_contents("php://input"), true);
    if (!isset($data['name'])) {
        http_response_code(400);
        echo json_encode(["error" => "Nom requis"]);
        exit;
    }
    $users = readUsers($filename);
    $newUser = [
        "id" => time(),
        "name" => $data['name']
    ];
    $users[] = $newUser;
    saveUsers($filename, $users);
    echo json_encode($newUser);
    exit;
}

if ($method === 'PUT') {
    parse_str($_SERVER['QUERY_STRING'], $query);
    $id = $query['id'] ?? null;
    if (!$id) {
        http_response_code(400);
        echo json_encode(["error" => "ID requis"]);
        exit;
    }
    $data = json_decode(file_get_contents("php://input"), true);
    $users = readUsers($filename);
    foreach ($users as &$user) {
        if ($user['id'] == $id) {
            $user['name'] = $data['name'] ?? $user['name'];
            saveUsers($filename, $users);
            echo json_encode($user);
            exit;
        }
    }
    http_response_code(404);
    echo json_encode(["error" => "Utilisateur non trouvé"]);
    exit;
}

if ($method === 'DELETE') {
    parse_str($_SERVER['QUERY_STRING'], $query);
    $id = $query['id'] ?? null;
    if (!$id) {
        http_response_code(400);
        echo json_encode(["error" => "ID requis"]);
        exit;
    }
    $users = readUsers($filename);
    $filtered = array_filter($users, fn($u) => $u['id'] != $id);
    if (count($users) == count($filtered)) {
        http_response_code(404);
        echo json_encode(["error" => "Utilisateur non trouvé"]);
        exit;
    }
    saveUsers($filename, array_values($filtered));
    echo json_encode(["message" => "Utilisateur supprimé"]);
    exit;
}
?>
