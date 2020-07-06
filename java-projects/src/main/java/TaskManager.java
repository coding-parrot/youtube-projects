import com.google.inject.Inject;
import com.google.inject.Singleton;
import logger.Logger;

import java.util.concurrent.CompletableFuture;

@Singleton
public class TaskManager {
    private final Logger logger;

    @Inject
    public TaskManager(final Logger logger) {
        this.logger = logger;
    }

    public CompletableFuture<Void> execute() {
        final String[] sentence = "This is a tutorial on Dependency Injection!".split(" ");
        for (final String word : sentence) {
            logger.write(word);
        }
        return logger.flushAsync()
                .whenComplete((__, throwable) -> {
                    if (throwable != null) {
                        throwable.printStackTrace();
                    } else {
                        logger.close();
                    }
                });
    }
}
