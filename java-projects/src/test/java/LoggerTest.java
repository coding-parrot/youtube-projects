import javafx.collections.transformation.SortedList;
import logger.LogClient;
import logger.LogClientImpl;
import org.junit.Assert;
import org.junit.Test;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;

public class LoggerTest {
    @Test
    public void defaultLogging() throws InterruptedException, ExecutionException {
        final TestTimer timer = new TestTimer();
        final LogClient logClient = new LogClientImpl(timer);
        List<CompletableFuture<Void>> tasks = new ArrayList<>();
        addTask(() -> logClient.start("1", 1), tasks);
        passOneSecond(timer);
        addTask(() -> logClient.start("2", 2), tasks);
        passOneSecond(timer);
        addTask(() -> logClient.start("3", 3), tasks);
        CompletableFuture.allOf(tasks.toArray(CompletableFuture[]::new)).get();
        tasks.clear();
        passOneSecond(timer);
        addTask(() -> logClient.end("3"), tasks);
        passOneSecond(timer);
        addTask(() -> logClient.end("2"), tasks);
        passOneSecond(timer);
        passOneSecond(timer);
        addTask(() -> System.out.println(logClient.poll()), tasks);
        passOneSecond(timer);
        addTask(() -> System.out.println(logClient.poll()), tasks);
        passOneSecond(timer);
        addTask(() -> logClient.end("1"), tasks);
        addTask(() -> System.out.println(logClient.poll()), tasks);
        CompletableFuture.allOf(tasks.toArray(CompletableFuture[]::new)).get();
        tasks.clear();
    }

    @Test
    public void concurrencyTest() throws ExecutionException, InterruptedException {
        final TestTimer timer = new TestTimer();
        final LogClient logClient = new LogClientImpl(timer);
        final ExecutorService executorService = Executors.newFixedThreadPool(5000);
        final Random random = new Random();
        final List<String> commands = new ArrayList<>();
        for (int i = 0; i < 5; i++) {
            commands.add("POLL");
            commands.add("END " + i);
        }
        Collections.shuffle(commands);
        int index = 0;
        while (index < commands.size()) {
            if (!commands.get(index).equals("POLL")) {
                commands.add(random.nextInt(index + 1), "START " + commands.get(index).split(" ")[1]);
                index++;
            }
            index++;
        }
        List<String> results = new CopyOnWriteArrayList<>();
        List<CompletableFuture<Void>> tasks = new CopyOnWriteArrayList<>();
        for (final String command : commands) {
            if (command.equals("POLL")) {
                tasks.add(CompletableFuture.supplyAsync(logClient::poll, executorService).thenAccept(results::add));
            } else {
                final var id = command.split(" ")[1];
                if (command.startsWith("START ")) {
                    logClient.start(id, (Long.parseLong(id) + 1) * 1000);
                } else {
                    logClient.end(id);
                }
            }
        }
        CompletableFuture.allOf(tasks.toArray(CompletableFuture[]::new)).get();
        for (int i = 0; i < results.size(); i++) {
            final var s = results.get(i);
            System.out.println(s);
            Assert.assertTrue(s.startsWith("task " + i + " started at:"));
        }
    }

    private void addTask(Runnable task, List<CompletableFuture<Void>> tasks) {
        tasks.add(CompletableFuture.runAsync(task));
    }

    private void passOneSecond(TestTimer timer) {
        passTime(timer, Duration.ofSeconds(1).toMillis());
    }

    private void passTime(TestTimer timer, long duration) {
        timer.setCurrentTime(timer.getCurrentTime() + duration);
    }
}

class Statement {
    String id;
    int start, end;
}