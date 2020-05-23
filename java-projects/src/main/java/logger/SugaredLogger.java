package logger;

import exceptions.LoggingException;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class SugaredLogger {
    private static SugaredLogger SUGARED_LOGGER;
    private final String identifier;
    private final OutputStream stream;
    private final List<String> buffer;

    private SugaredLogger(final OutputStream stream) {
        this.stream = stream;
        identifier = "service:";
        buffer = new ArrayList<>();
    }


    public static synchronized SugaredLogger getLogger(OutputStream out) {
        if (SUGARED_LOGGER == null) {
            SUGARED_LOGGER = new SugaredLogger(out);
        }
        return SUGARED_LOGGER;
    }

    public boolean write(final String word) {
        buffer.add(identifier + " " + word + "\n");
        return true;
    }

    public CompletableFuture<Void> flushAsync() {
        CompletableFuture<Void> result = CompletableFuture.completedFuture(null);
        ExecutorService service = Executors.newSingleThreadExecutor();
        for (final String word : buffer) {
            result = result.thenAcceptAsync(__ -> {
                try {
                    Thread.sleep(1000);
                    stream.write(word.getBytes());
                } catch (IOException | InterruptedException e) {
                    e.printStackTrace();
                }
            }, service);
        }
        return result;
    }

    public boolean close() {
        try {
            stream.flush();
            stream.close();
        } catch (IOException e) {
            throw new LoggingException(e);
        }
        return false;
    }
}
