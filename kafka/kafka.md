# Kafka

## What is Kafka

### Purpose

Kafka is mainly used to exchange data between systems, it does not replace
databases, key-value stores, or search engines.

### Log

Kafka is a distributed log, in which data is stored in topics, sharded into
partitions that allow topics to scale horizontally and parallel processing.


A log is an ordered list of timestamped and immutable elements where elements
are added at the end, and read from a specific position (offsets).

## Design

### Components of Kafka

A Kafka cluster is made of 3 components:
 * coordination cluster
     * checks brokers are still reachable and functional, add new brokers and
         remove existing brokers when necessary
    * was previously done by Zookeeper
    * coordination role can be fulfilled by brokers
    * there should be 3 or 5 nodes (for increased reliability)
 * brokers
     * receive, store, and make messages available for retrieval
     * one broker acts as a controller, which is responsible for managing state
         of partitions and replicas (e.g. assign brokers to partitions and
         designate a partition leader)
 * clients
    * any producer or consumer

Producers write to topics, and can control to which partitions messages are
written to via keys (messages with the same key end up in the same partition).

Consumer groups are used to scale consumers and share the workload. One
partition is consumed by one and only one consumer within a group.

### Replication

Data from topics is replicated: it is copied to other brokers. Replication is
configurable at the topic level, each topic can have a different replication
factor.

Kafka replication follow the "one leader-several followers" strategy. Each
partition has its own leader and followers. If we have a topic replication
factor of 3, each partition will have one leader and two followers.

Producers and consumers interact with the leader broker. Followers replicate
data by requesting topic messages from the leader. Followers inform the leader
of their current offset, so the leader knows when a follower has consumed a
message.

When the partition leader fails, another leader is elected among in-sync
replicas or eligible leader replicas.

Use the tool `kafka-topics.sh` with the parameters
`--under-replicated-partitions` or `--under-min-isr-partitions` to debug
replication issues.

Kafka topics have a 'preferred leader', which is shown at the top of the
replica list.

The tool `kafka-leader-election.sh` can be used to rebalance leaders manually.
The argument `--election-type` (required) controls how the leader is elected:
`preferred` used the preferred leader, and `unclean` allows to select a leader
among non-in-sync replicas (only to use in extreme circumstances because this
can lead to data loss!).

### Producers

#### Message acknowledgements

Producers use acknowledgements (ACKs) to confirm a message has been
successfully sent to a broker.

There are three producer configuration options:
* `acks=all`: partition leader sends ACK to producer after all in-sync replicas have
    replicated the message. Highest reliability. Data loss may occur if all
    replicas are on the same rack and the rack power source fails (Kafka does
    not immediately flush messages to disk, but relies on OS page cache for
    high performance). This is the default setting.
* `acks=1`: broker sends ACK to producer as soon as it receives it. Data loss
    may occur if the leader fails immediately after ACK.
* `acks=0`: no ACK is sent. Highest performance but lowest reliability.

For `acks=all`, `min.insync.replicas` must replicate the message before an ACK
is sent. If not enough replicas are reachable or in sync, the producer receives
the error `NOT_ENOUGH_REPLICAS` and retries to sent the message.

![Producer ACKs](producer-acks.png)

#### Delivery guarantees

At-most-once delivery is achieved with `acks=0`. Messages may be lost.

At-least-once delivery is achieved by setting `min.insync.replicas` to a
reasonable value (e.g. 2) and `acks=all`. Duplication may occur.

Exactly-once delivery is achieved with `acks=all` and
`enable.idempotence=true` (`max.in.flight.requests.per.connection` must be at
most 5 because broker only retains at most 5 batches for each producer, and
`retries` must be greater than 0). Idempotence is implemented with the producer
sending a sequence ID along with each message, so that the broker can ignore
duplicate sequence IDs, and ensure that messages are received in the correct
order). If duplicate messages arrive to the broker, only ACK is resent and
message is not persisted. If messages arrive out of order, NACK (negative ACK)
is sent, and the producer should retry.

#### Transactions

See [documentation](https://kafka.apache.org/documentation/#usingtransactions).

Transactions allow atomic writes across multiple partitions, for example to
consume a message from one topic, then write it to another topic atomically.

The producer must set the property `transactional.id`, and ensure that
different producers use different transactional IDs.

When a consumer is involved in the transaction, the important part is to use
the consumer configuration `enable.auto.commit=false` to avoid advancing
committed offsets outside of the transaction. Then, after the consumed message
has been processed and produced to another topic, we call the producer method
`send_offsets_to_transaction()` to commit offsets as part of the transaction.

The consumer `isolation.level` must be set to `read_committed`.
This is because Kafka transactions work similarly to two-phase
commits, where messages are first produced and then confirmed using commit
markers, or rollbacked using abort markers. If `isolation.level` is set to
`read_uncommited`, consumers would see rollbacked messages.

See this [Python
snippet](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/eos_transactions.py)
to see how transactions can be implemented in the producer and consumer.

This is how Kafka Streams work.

## Data schema

Confluent Schema Registry is part of Confluent Enterprise.

[Karapace](https://github.com/Aiven-Open/karapace) is an open-source
alternative, and also serves as a Kafka REST proxy.

## Gotchas

### Message partitioning

The library `librdkafka` (used by the Python client library) uses a different
hash algorithm than the Java client library. If both languages are used to
produce to the same topics, messages may be partitioned inconsistently. To
ensure correctness, one should set the partitioner to `murmur2_random` in
`librdkafka` producers. 

### Consumer parallelism

Consumers a part of a group in which topic partitions are distributed across
members of the group, each partition being consumed by one and only one member.
Therefore, the maximum number of consumers in a group should be the number of
partitions, otherwise there will be idle consumers with no partition.

Reducing the number of partitions is not possible as this would result in data
loss. Reducing the number of partitions would mean that some messages would
move to new partitions, and this would break message ordering guarantees.

## Important configuration properties

[Reference](https://kafka.apache.org/documentation/)

### Topic

* `min.insync.replicas`: Minimum number of replicas that must acknowledge a
    write for the write to be considered successful (i.e. for leader to send
    ACK back to prodcer). Messages are visible to consumers after they are
    replicated to all in-sync replicas and `min.insync.replicas` is met. A
    typical configuration is a replication factor of 3 and
    `min.insync.replicas` equal to 2.

### Producer

* `acks`: Number of acknowledgements the leader requires before it considers a
    request complete. Can be `all`, `1`, or `0`. `all` is required for
    idempotence. Default is `all`.
* `enable.idempotence`: To ensure that the producer will send exactly one copy
    of each message to a topic. Default is `true`.
* `max.in.flight.requests.per.connection`: Maximum number of unacknowledged
    requests the client will send on a single connection before blocking.
* `transactional.id`: Ensure that transactions using the same ID have been
    completed before starting new transactions. Default is null (transactions
    are disabled).

### Consumer

* `enable.auto.commit`: Allow the consumer to periodically commit offsets in
    the brackground (default is true). Must be set to false when a consumer
    takes part in producer transactions.
* `isolation.level`: If set to `read_committed`, `consumer.poll()` only returns
    committed transactional messages. With `read_uncommitted` (default), all
    messages are  returned.
