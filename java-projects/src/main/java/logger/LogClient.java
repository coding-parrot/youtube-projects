package logger;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public interface LogClient {
    /**
     * When a process starts, it calls 'start' with processId.
     */
    void start(String processId, long timestamp);

    /**
     * When the same process ends, it calls 'end' with processId.
     */
    void end(String processId);

    /**
     * Polls the first log entry of a completed process sorted by the start time of processes in the below format
     * {processId} started at {startTime} and ended at {endTime}
     * <p>
     * process id = 1 --> 12, 15
     * process id = 2 --> 8, 12
     * process id = 3 --> 7, 19
     * <p>
     * {3} started at {7} and ended at {19}
     * {2} started at {8} and ended at {12}
     * {1} started at {12} and ended at {15}
     */
    String poll();
}

class LoggerImplementation implements LogClient {

    private final Map<String, Process> processes;
    private final ConcurrentSkipListMap<Long, Process> queue;
    private final List<CompletableFuture<Void>> futures;
    private final Lock lock;
    private final ExecutorService[] taskScheduler;

    public LoggerImplementation() {
        this.processes = new ConcurrentHashMap<>();
        this.queue = new ConcurrentSkipListMap<>();
        this.futures = new CopyOnWriteArrayList<>();
        this.lock = new ReentrantLock();
        this.taskScheduler = new ExecutorService[10];
        for (int i = 0; i < taskScheduler.length; i++) {
            taskScheduler[i] = Executors.newSingleThreadExecutor();
        }
    }

    @Override
    public void start(String processId, long timestamp) { //1
        taskScheduler[processId.hashCode() % taskScheduler.length].execute(() -> {
            final long now = System.currentTimeMillis();    //1
            final Process process = new Process(processId, now);
            processes.put(processId, process);
            queue.put(now, process);
        });
    }

    @Override
    public void end(String processId) { //1
        taskScheduler[processId.hashCode() % taskScheduler.length].execute(() -> {
            lock.lock();//1
            try {
                final long now = System.currentTimeMillis();//1
                processes.get(processId).setEndTime(now);//1
                if (!futures.isEmpty() && queue.firstEntry().getValue().getId().equals(processId)) {
                    pollNow();
                    final var result = futures.remove(0);
                    result.complete(null);
                }
            } finally {
                lock.unlock();
            }
        });
    }

    @Override
    public String poll() {
        lock.lock();
        try {
            final var result = new CompletableFuture<Void>();
            if (!queue.isEmpty() && queue.firstEntry().getValue().getEndTime() != -1) {
                pollNow();
            } else {
                futures.add(result);
            }
            try {
                result.get(3, TimeUnit.SECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                throw new RuntimeException(e);
            }
            return null;
        } finally {
            lock.unlock();
        }
    }

    private String pollNow() {
        final Process process = queue.firstEntry().getValue();
        final var logStatement = process.getId() + " started at " + process.getStartTime() + " and ended at " + process.getEndTime();
        System.out.println(logStatement);
        processes.remove(process.getId());
        queue.pollFirstEntry();
        return logStatement;
    }
}

class Process {
    private final String id;
    private final long startTime;
    private long endTime;

    public Process(final String id, final long startTime) {
        this.id = id;
        this.startTime = startTime;
        endTime = -1;
    }

    public String getId() {
        return id;
    }

    public long getStartTime() {
        return startTime;
    }

    public long getEndTime() {
        return endTime;
    }

    public void setEndTime(long endTime) {
        this.endTime = endTime;
    }
}

class LoggerMain {
    /*
     * {3} started at {7} and ended at {19}
     * {2} started at {8} and ended at {12}
     * {1} started at {12} and ended at {15}
     */
    public static void main(String[] args) {
        final LogClient logger = new LoggerImplementation();
        logger.start("1", 1);
        logger.poll();
        logger.start("3", 2);
        logger.poll();
        logger.end("1");
        logger.poll();
        logger.start("2", 3);
        logger.poll();
        logger.end("2");
        logger.poll();
        logger.end("3");
        logger.poll();
        logger.poll();
        logger.poll();
        //1
        //3
        //2
    }
}