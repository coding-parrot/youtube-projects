package logger;

import java.util.Comparator;
import java.util.HashMap;
import java.util.Map;
import java.util.TreeMap;

interface LogClient {
    /**
     * When a process starts, it calls 'start' with processId.
     */
    void start(String processId);

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
    void poll();
}

class LoggerImplementation implements LogClient {

    private final Map<String, Process> processes;
    private final TreeMap<Long, Process> queue;

    public LoggerImplementation() {
        this.processes = new HashMap<>();
        this.queue = new TreeMap<>(Comparator.comparingLong(startTime -> startTime));
    }

    @Override
    public void start(String processId) {
        final long now = System.currentTimeMillis();
        final Process process = new Process(processId, now);
        processes.put(processId, process);
        queue.put(now, process);
    }

    @Override
    public void end(String processId) {
        final long now = System.currentTimeMillis();
        processes.get(processId).setEndTime(now);
    }

    @Override
    public void poll() {
        if (queue.isEmpty()){
            System.out.println("Queue is empty");
            return;
        }
        final Process process = queue.firstEntry().getValue();
        if (process.getEndTime() != -1) {
            System.out.println(process.getId() + " started at " + process.getStartTime() + " and ended at " + process.getEndTime());
            processes.remove(process.getId());
            queue.pollFirstEntry();
        } else {
            System.out.println("No completed tasks in queue. " + queue.size());
        }
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
        logger.start("1");
        logger.poll();
        logger.start("3");
        logger.poll();
        logger.end("1");
        logger.poll();
        logger.start("2");
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