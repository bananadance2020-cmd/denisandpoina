<?php
$request_uri = $_SERVER['REQUEST_URI'];
$method = $_SERVER['REQUEST_METHOD'];

// Handle VK Link
if (strpos($request_uri, '/link_vk.php') !== false && $method === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    if ($data && isset($data['secret_key']) && $data['secret_key'] === 'super_secret_wedding_key_2024') {
        file_put_contents('vk_config.json', json_encode(['user_id' => $data['user_id']]));
        header('Content-Type: application/json');
        echo json_encode(['status' => 'success']);
        exit;
    }
    http_response_code(400);
    exit;
}

// Handle Form Submission
if (strpos($request_uri, '/submit_form') !== false && $method === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);
    
    $user_id = "156300398"; // ID клиента по умолчанию
    if (file_exists('vk_config.json')) {
        $config = json_decode(file_get_contents('vk_config.json'), true);
        if (isset($config['user_id'])) {
            $user_id = $config['user_id'];
        }
    }
    
    if ($user_id) {
            $vk_token = "vk1.a.GZqjYnIiyHtMKq7UfWz3-SzU5KabyxA40z0cu-FHiQ7_wxHTl5rSXRwm0IcLR2gk0ebpDhmZNsoIcDTIvMAcHJL1EOAJB87HSIjUdqpmdO7_BK2UR5wNfVHI1D2EmcSJs-Q_tolKJI41OwPubAGcyUc5HGcRewdp8kq0fD67OvxsW4PC4ICijUiolvzRZPdluCT1jKsEMn0AbGI3VbPEXQ";
            
            $message = "🔔 Новая анкета от гостя!\n\n";
            foreach ($data as $key => $val) {
                if ($val !== '' && $val !== null) {
                    $message .= "• {$key}: {$val}\n";
                }
            }
            
            $params = http_build_query([
                'message' => $message,
                'peer_id' => $user_id,
                'access_token' => $vk_token,
                'v' => '5.131',
                'random_id' => mt_rand()
            ]);
            
            file_get_contents("https://api.vk.com/method/messages.send?" . $params);
        }
    }
    
    header('Content-Type: application/json');
    echo json_encode(['status' => 'ok']);
    exit;
}

// Standard Eventrix proxying
$target_url = "https://eventrix.pro" . $request_uri;
$ch = curl_init($target_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, true);

    // Фейковый успешный ответ для внутренней формы Eventrix
    if (strpos($request_uri, '/api/') !== false) {
        $input = file_get_contents('php://input');
        
        // Попытаемся отправить эти данные в VK
        if (strpos($request_uri, 'submit') !== false || strpos($request_uri, 'form') !== false) {
            $data = json_decode($input, true);
            $user_id = "156300398"; // ID клиента по умолчанию
            
            if (file_exists('vk_config.json')) {
                $config = json_decode(file_get_contents('vk_config.json'), true);
                if (isset($config['user_id'])) {
                    $user_id = $config['user_id'];
                }
            }
            
            if ($user_id && $data) {
                $vk_token = "vk1.a.GZqjYnIiyHtMKq7UfWz3-SzU5KabyxA40z0cu-FHiQ7_wxHTl5rSXRwm0IcLR2gk0ebpDhmZNsoIcDTIvMAcHJL1EOAJB87HSIjUdqpmdO7_BK2UR5wNfVHI1D2EmcSJs-Q_tolKJI41OwPubAGcyUc5HGcRewdp8kq0fD67OvxsW4PC4ICijUiolvzRZPdluCT1jKsEMn0AbGI3VbPEXQ";
                $message = "🔔 Новая анкета от гостя (Native)!\n\n";
                
                $fields = isset($data['fields']) ? $data['fields'] : $data;
                foreach ($fields as $key => $val) {
                    if ($val !== '' && $val !== null) {
                        $message .= "• {$key}: {$val}\n";
                    }
                }
                
                $params = http_build_query([
                    'message' => $message,
                    'peer_id' => $user_id,
                    'access_token' => $vk_token,
                    'v' => '5.131',
                    'random_id' => mt_rand()
                ]);
                
                file_get_contents("https://api.vk.com/method/messages.send?" . $params);
            }
        }
        
        header('Content-Type: application/json');
        echo json_encode(['success' => true, 'status' => 'ok', 'message' => 'success']);
        exit;
    }
    
    curl_setopt($ch, CURLOPT_POST, true);
    $input = file_get_contents('php://input');
    if ($input) {
        curl_setopt($ch, CURLOPT_POSTFIELDS, $input);
    }
    $headers_in = [];
    foreach (getallheaders() as $name => $value) {
        if (strtolower($name) === 'content-type') {
            $headers_in[] = "$name: $value";
        }
    }
    if (!empty($headers_in)) {
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers_in);
    }
}

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
$headers = substr($response, 0, $header_size);
$body = substr($response, $header_size);
curl_close($ch);

$header_lines = explode("\r\n", $headers);
foreach ($header_lines as $header) {
    if (stripos($header, 'Transfer-Encoding') === 0) continue;
    if (stripos($header, 'Content-Encoding') === 0) continue;
    if (stripos($header, 'Access-Control-Allow-Origin') === 0) continue;
    if (!empty($header)) {
        header($header);
    }
}
header('Access-Control-Allow-Origin: *');

// Remove watermark and reorder layout in JSON
if (strpos($request_uri, '/api/invites/get/byURL') !== false) {
    $data = json_decode($body, true);
    if ($data && isset($data['data'])) {
        $data['data']['purchased'] = true;
        $data['data']['published'] = true;
        
        if (isset($data['data']['blocks'])) {
            $blocks = $data['data']['blocks'];
            $wishes_idx = -1;
            
            foreach ($blocks as $i => $b) {
                if (isset($b['id']) && $b['id'] === 'Wishes') $wishes_idx = $i;
            }
            
            if ($wishes_idx !== -1) {
                $w_block = $blocks[$wishes_idx];
                array_splice($blocks, $wishes_idx, 1);
                
                $dresscode_idx = -1;
                foreach ($blocks as $i => $b) {
                    if (isset($b['id']) && $b['id'] === 'DressCode') $dresscode_idx = $i;
                }
                
                if ($dresscode_idx !== -1) {
                    array_splice($blocks, $dresscode_idx + 1, 0, [$w_block]);
                }
                $data['data']['blocks'] = $blocks;
            }
        }
        
        $body = json_encode($data);
    }
}

echo $body;
