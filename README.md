Background:
- `Ingress` has a handle to `Inference`
- `Ingress` has 1 worker, `Inference` one has 10 workers
- `client.py` dispatches 10 concurrent requests
- 1 machine, 16 CPU cores available

Questions:
- Why are all not all the print calls from insider `Ingress` (denoted with `[WORKER]`) printed?
- There are a few inference calls that only take ~25ms. 
    - Why do all the ingress timings at least 60ms? Is that extra 30ms of time being added by Ray?
    - Are multiple requests being routed to the same `Inference` replica?
    - If so, what's the point of defining `num_replicas` if Ray won't uniformly distribute the load?


```
(HTTPProxyActor pid=268697) INFO:     ('127.0.0.1', 45552) - "WebSocket /" [accepted]
(HTTPProxyActor pid=268697) INFO:     connection open
(ServeReplica:default_Inference pid=268749) INFO 2023-08-02 18:07:03,519 default_Inference default_Inference#mtylLG oQzRSNNGan / default replica.py:723 - __CALL__ OK 62.0ms
(ServeReplica:default_Inference pid=268749) INFO 2023-08-02 18:07:03,545 default_Inference default_Inference#mtylLG oQzRSNNGan / default replica.py:723 - __CALL__ OK 24.7ms
(ServeReplica:default_Inference pid=268749) [WORKER] Took 0.024555683135986328 seconds to compute logits. [repeated 51x across cluster]
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06375503540039062 seconds to complete request 329934e0-abdc-4887-a54f-92872a2ffb3f.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.0649104118347168 seconds to complete request d443f21d-aa7e-417f-a217-a823251d9324.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06409120559692383 seconds to complete request b69f1ede-269f-4a34-8d20-65ab83a7dd81.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06693530082702637 seconds to complete request 6b0b52fe-162f-491a-8283-d25f026a9b69.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06712460517883301 seconds to complete request c980ae01-32b6-4ccc-9653-b6db9773d14e.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06794095039367676 seconds to complete request 62449a33-474f-48d0-917c-4fc5c7e36288.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.06844472885131836 seconds to complete request b5304c68-06ca-4b9b-8487-b40193c10886.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.09019851684570312 seconds to complete request 6efd2f1c-0378-46c2-9e2f-4e706dde79f6.
(ServeReplica:default_Inference pid=268753) INFO 2023-08-02 18:07:03,520 default_Inference default_Inference#AVgvoQ oQzRSNNGan / default replica.py:723 - __CALL__ OK 62.9ms
(ServeReplica:default_Inference pid=268750) INFO 2023-08-02 18:07:03,515 default_Inference default_Inference#rLlVGC oQzRSNNGan / default replica.py:723 - __CALL__ OK 59.4ms
(ServeReplica:default_Inference pid=268755) INFO 2023-08-02 18:07:03,521 default_Inference default_Inference#IEpFZe oQzRSNNGan / default replica.py:723 - __CALL__ OK 62.7ms
(ServeReplica:default_Inference pid=268752) INFO 2023-08-02 18:07:03,515 default_Inference default_Inference#LqbCcH oQzRSNNGan / default replica.py:723 - __CALL__ OK 58.6ms
(ServeReplica:default_Inference pid=268738) INFO 2023-08-02 18:07:03,519 default_Inference default_Inference#bCbldh oQzRSNNGan / default replica.py:723 - __CALL__ OK 62.5ms
(ServeReplica:default_Inference pid=268748) INFO 2023-08-02 18:07:03,515 default_Inference default_Inference#gqyjPm oQzRSNNGan / default replica.py:723 - __CALL__ OK 58.3ms
(ServeReplica:default_Inference pid=268748) INFO 2023-08-02 18:07:03,542 default_Inference default_Inference#gqyjPm oQzRSNNGan / default replica.py:723 - __CALL__ OK 25.9ms
(HTTPProxyActor pid=268697) INFO:     connection closed
(ServeReplica:default_Inference pid=268749) INFO 2023-08-02 18:07:03,566 default_Inference default_Inference#mtylLG oQzRSNNGan / default replica.py:723 - __CALL__ OK 21.3ms
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.11423301696777344 seconds to complete request d4bd4f78-ace7-4a1f-926b-8b1b1f5f633e.
(ServeReplica:default_Ingress pid=268756) [INGRESS] Took 0.11437821388244629 seconds to complete request 286a1803-76c2-4bea-b969-ddff50923239.
(ServeReplica:default_Ingress pid=268756) Client disconnected.
(ServeReplica:default_Ingress pid=268756) INFO 2023-08-02 18:07:03,569 default_Ingress default_Ingress#OmwEVs oQzRSNNGan / default replica.py:723 - __CALL__ OK 120.1ms
```

```
Took 0.06707334518432617 seconds for request 329934e0-abdc-4887-a54f-92872a2ffb3f to be fulfilled.
Took 0.06737732887268066 seconds for request d443f21d-aa7e-417f-a217-a823251d9324 to be fulfilled.
Took 0.06707978248596191 seconds for request b69f1ede-269f-4a34-8d20-65ab83a7dd81 to be fulfilled.
Took 0.06934118270874023 seconds for request 6b0b52fe-162f-491a-8283-d25f026a9b69 to be fulfilled.
Took 0.06924915313720703 seconds for request c980ae01-32b6-4ccc-9653-b6db9773d14e to be fulfilled.
Took 0.06953263282775879 seconds for request 62449a33-474f-48d0-917c-4fc5c7e36288 to be fulfilled.
Took 0.0698697566986084 seconds for request b5304c68-06ca-4b9b-8487-b40193c10886 to be fulfilled.
Took 0.09227132797241211 seconds for request 6efd2f1c-0378-46c2-9e2f-4e706dde79f6 to be fulfilled.
Took 0.1163175106048584 seconds for request d4bd4f78-ace7-4a1f-926b-8b1b1f5f633e to be fulfilled.
Took 0.11629104614257812 seconds for request 286a1803-76c2-4bea-b969-ddff50923239 to be fulfilled.
[{'id': 'd443f21d-aa7e-417f-a217-a823251d9324', 'start': 1691024823.4519286, 'logits': [[-0.11890064179897308, 0.08033183962106705]]}, {'id': '6b0b52fe-162f-491a-8283-d25f026a9b69', 'start': 1691024823.4520264, 'logits': [[-0.02248799428343773, -0.021837597712874413]]}, {'id': 'c980ae01-32b6-4ccc-9653-b6db9773d14e', 'start': 1691024823.45214, 'logits': [[-0.0276297926902771, 0.11271484941244125]]}, {'id': '329934e0-abdc-4887-a54f-92872a2ffb3f', 'start': 1691024823.4521916, 'logits': [[0.018737144768238068, -0.05270552635192871]]}, {'id': 'b69f1ede-269f-4a34-8d20-65ab83a7dd81', 'start': 1691024823.4522426, 'logits': [[-0.11278679221868515, 0.06468745321035385]]}, {'id': '62449a33-474f-48d0-917c-4fc5c7e36288', 'start': 1691024823.4522882, 'logits': [[0.1064518615603447, -0.03943554684519768]]}, {'id': 'd4bd4f78-ace7-4a1f-926b-8b1b1f5f633e', 'start': 1691024823.4523306, 'logits': [[-0.02706400863826275, 0.12094366550445557]]}, {'id': '286a1803-76c2-4bea-b969-ddff50923239', 'start': 1691024823.4523768, 'logits': [[-0.04014109447598457, 0.11138756573200226]]}, {'id': '6efd2f1c-0378-46c2-9e2f-4e706dde79f6', 'start': 1691024823.4524207, 'logits': [[-0.09290292859077454, 0.04749571159482002]]}, {'id': 'b5304c68-06ca-4b9b-8487-b40193c10886', 'start': 1691024823.4524636, 'logits': [[0.0392649807035923, -0.048447370529174805]]}]
```