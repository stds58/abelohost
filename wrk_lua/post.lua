wrk.method = "POST"
wrk.headers["Content-Type"] = "application/json"
wrk.body   = '{"data": "test_payload_for_load_testing"}'

function request()
    return wrk.format("POST", nil, nil, payload)
end