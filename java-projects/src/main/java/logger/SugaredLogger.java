package logger;

import com.google.inject.Inject;
import com.google.inject.Singleton;
import com.google.inject.name.Named;
import exceptions.LoggingException;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Singleton
public class SugaredLogger implements Logger {
    private final String identifier;
    private final OutputStream stream;
    private final List<String> buffer;

    @Inject
    public SugaredLogger(final OutputStream stream, @Named("logger.fast.identifier")  String identifier) {
        this.stream = stream;
        this.identifier = identifier;
        buffer = new ArrayList<>();
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
