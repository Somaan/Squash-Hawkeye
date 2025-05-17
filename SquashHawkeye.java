import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.*;
import javax.imageio.ImageIO;
import javax.sound.sampled.*;
import javax.swing.*;
import java.util.ArrayList;
import java.util.List;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;

public class SquashHawkeye extends JFrame {
    private JPanel videoPanel;
    private JLabel statusLabel;
    private JProgressBar progressBar;
    private List<Double> impactTimestamps = new ArrayList<>();
    private File videoFile;
    private File audioFile;
    private String ffmpegPath = "C:\\ffmpeg-clean\\ffmpeg-7.1.1-full_build\\bin\\ffmpeg.exe";
    private String defaultVideoPath = "test_17.mp4";
    private boolean debugMode = true;

    public SquashHawkeye() {
        super("Squash Hawk-Eye System");
        initUI();

        SwingUtilities.invokeLater(() -> loadDefaultVideo());
    }

    private void debug(String message) {
        if (debugMode) {
            System.out.println("[DEBUG] " + message);
        }
    }

    private void initUI() {
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(800, 600);
        setLayout(new BorderLayout());

        videoPanel = new JPanel();
        videoPanel.setBackground(Color.BLACK);
        add(videoPanel, BorderLayout.CENTER);

        JPanel controlPanel = new JPanel(new BorderLayout());
        JPanel statusPanel = new JPanel(new BorderLayout());
        statusLabel = new JLabel("Starting automatic analysis...");
        progressBar = new JProgressBar(0, 100);
        progressBar.setStringPainted(true);

        statusPanel.add(statusLabel, BorderLayout.NORTH);
        statusPanel.add(progressBar, BorderLayout.SOUTH);
        controlPanel.add(statusPanel, BorderLayout.CENTER);
        add(controlPanel, BorderLayout.SOUTH);
    }

    private void loadDefaultVideo() {
        videoFile = new File(defaultVideoPath);

        if (!videoFile.exists()) {
            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setFileFilter(new javax.swing.filechooser.FileNameExtensionFilter(
                "Video Files", "mp4", "avi", "mov"));

            int result = fileChooser.showOpenDialog(this);
            if (result == JFileChooser.APPROVE_OPTION) {
                videoFile = fileChooser.getSelectedFile();
                statusLabel.setText("Selected: " + videoFile.getName());
                analyzeAndCapture();
            } else {
                statusLabel.setText("No video selected. Exiting...");
                Timer timer = new Timer(2000, e -> System.exit(0));
                timer.setRepeats(false);
                timer.start();
            }
        } else {
            statusLabel.setText("Loaded default video: " + videoFile.getName());
            analyzeAndCapture();
        }
    }

    private void analyzeAndCapture() {
        if (videoFile == null) return;

        SwingWorker<Void, Object[]> worker = new SwingWorker<Void, Object[]>() {
            protected Void doInBackground() throws Exception {
                publish(new Object[]{"Step 1: Extracting audio from video...", 10});
                if (!extractAudio()) {
                    publish(new Object[]{"Failed to extract audio from video.", 0});
                    return null;
                }

                publish(new Object[]{"Step 2: Analysing audio for impacts...", 40});
                detectImpacts();

                if (impactTimestamps.isEmpty()) {
                    publish(new Object[]{"No impacts detected in the audio.", 50});
                    return null;
                }

                publish(new Object[]{"Step 3: Extracting all video frames...", 60});
                double fps = extractVideoInfo();

                publish(new Object[]{"Step 4: Capturing screenshots at impact points...", 80});
                captureFramesAtImpacts(fps);

                return null;
            }

            protected void process(List<Object[]> chunks) {
                for (Object[] update : chunks) {
                    statusLabel.setText((String) update[0]);
                    progressBar.setValue((Integer) update[1]);
                    System.out.println((String) update[0]);
                }
            }

            protected void done() {
                try {
                    get();
                    statusLabel.setText("Processing complete! " + impactTimestamps.size() + " impacts detected and captured.");
                    progressBar.setValue(100);

                    Timer timer = new Timer(3000, e -> {
                        dispose();
                        System.exit(0);
                    });
                    timer.setRepeats(false);
                    timer.start();

                } catch (Exception e) {
                    statusLabel.setText("Error: " + e.getMessage());
                    e.printStackTrace();
                }
            }
        };

        worker.execute();
    }

    private boolean extractAudio() throws IOException, InterruptedException {
        audioFile = File.createTempFile("extracted_audio", ".wav");
        audioFile.deleteOnExit();
        debug("Extracting audio to: " + audioFile.getAbsolutePath());

        ProcessBuilder pb = new ProcessBuilder(ffmpegPath, "-i", videoFile.getAbsolutePath(), "-vn", "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2", "-y", audioFile.getAbsolutePath());
        pb.redirectErrorStream(true);
        Process process = pb.start();

        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        while ((line = reader.readLine()) != null) debug("FFmpeg: " + line);

        boolean completed = process.waitFor(30, java.util.concurrent.TimeUnit.SECONDS);
        if (!completed || process.exitValue() != 0 || !audioFile.exists() || audioFile.length() == 0) return false;
        System.out.println("Audio extraction successful: " + audioFile.length() + " bytes");
        return true;
    }

    private void detectImpacts() throws Exception {
        System.out.println("Analysing audio for impacts...");
        AudioInputStream audioStream = AudioSystem.getAudioInputStream(audioFile);
        AudioFormat format = audioStream.getFormat();
        byte[] audioData = audioStream.readAllBytes();
        audioStream.close();

        int bytesPerFrame = format.getFrameSize();
        int numSamples = audioData.length / bytesPerFrame;
        double maxAmplitude = 0;

        for (int i = 0; i < numSamples; i++) {
            short sample = getSampleValue(audioData, i * bytesPerFrame, format);
            maxAmplitude = Math.max(maxAmplitude, Math.abs(sample));
        }

        if (maxAmplitude == 0) return;

        double threshold = 0.7 * maxAmplitude;
        int minDistance = (int)(format.getSampleRate() * 0.2);
        int lastImpactSample = -minDistance;

        for (int i = 1; i < numSamples - 1; i++) {
            short sample = getSampleValue(audioData, i * bytesPerFrame, format);
            short prevSample = getSampleValue(audioData, (i - 1) * bytesPerFrame, format);
            short nextSample = getSampleValue(audioData, (i + 1) * bytesPerFrame, format);

            if (Math.abs(sample) > threshold && Math.abs(sample) > Math.abs(prevSample) && Math.abs(sample) >= Math.abs(nextSample) && i - lastImpactSample > minDistance) {
                double timeInSeconds = i / format.getSampleRate();
                impactTimestamps.add(timeInSeconds);
                lastImpactSample = i;
                System.out.println("Impact detected at " + String.format("%.3f", timeInSeconds) + " seconds");
            }
        }

        System.out.println("Found " + impactTimestamps.size() + " impacts");
    }

    private short getSampleValue(byte[] audioData, int sampleIndex, AudioFormat format) {
        if (sampleIndex + 1 >= audioData.length) return 0;
        return (short)((audioData[sampleIndex + 1] << 8) | (audioData[sampleIndex] & 0xFF));
    }

    private double extractVideoInfo() throws Exception {
        ProcessBuilder pb = new ProcessBuilder(ffmpegPath, "-i", videoFile.getAbsolutePath());
        pb.redirectErrorStream(true);
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        double fps = 25.0;

        while ((line = reader.readLine()) != null) {
            debug("FFmpeg info: " + line);
            if (line.contains(" fps,")) {
                for (String part : line.split("[,\s]")) {
                    part = part.trim();
                    if (part.endsWith("fps")) {
                        String fpsStr = part.replaceAll("[^0-9.]", "");
                        if (!fpsStr.isEmpty()) fps = Double.parseDouble(fpsStr);
                    }
                }
            }
        }
        process.waitFor();
        return fps;
    }

        private void captureFramesAtImpacts(double fps) {
        try {
            File screenshotDir = new File("impact_screenshots");
            if (!screenshotDir.exists()) {
                screenshotDir.mkdirs();
            } else {
                for (File file : screenshotDir.listFiles()) {
                    if (file.isFile()) {
                        file.delete();
                    }
                }
            }

            File framesDir = new File("frames");
            if (!framesDir.exists()) {
                framesDir.mkdirs();
            } else {
                for (File file : framesDir.listFiles()) {
                    if (file.isFile()) {
                        file.delete();
                    }
                }
            }

            for (int i = 0; i < impactTimestamps.size(); i++) {
                double timestamp = impactTimestamps.get(i);
                double startTime = Math.max(0, timestamp - 0.09); //speed of sound delay offset

                System.out.println("Impact " + (i + 1) + " at: " + timestamp + "s");

                String outputPath = String.format("impact_screenshots/impact_%.3f.png", timestamp).replace(":", "_");


                ProcessBuilder pb = new ProcessBuilder(
                    ffmpegPath,
                    "-i", videoFile.getAbsolutePath(),
                    "-ss", String.format("%.3f", startTime),
                    "-vframes", "1",
                    "-vf", "format=yuv420p",
                    "-pix_fmt", "rgb24",
                    "-q:v", "2",
                    "-f", "image2",
                    "-y",
                    outputPath
                );

                pb.redirectErrorStream(true);
                Process process = pb.start();

                BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
                String line;
                while ((line = reader.readLine()) != null) {
                    debug("FFmpeg: " + line);
                }

                int exitCode = process.waitFor();
                if (exitCode != 0) {
                    System.out.println("Error extracting frames. Exit code: " + exitCode);
                } else {
                    System.out.println("Frame saved to " + outputPath);
                }
            }
        } catch (Exception e) {
            System.out.println("Error capturing frames: " + e.getMessage());
            e.printStackTrace();
        }
    }
    public static void main(String[] args) {
        if (args.length > 0) {
            String videoPath = args[0];
            SwingUtilities.invokeLater(() -> {
                SquashHawkeye app = new SquashHawkeye();
                app.defaultVideoPath = videoPath;
                app.setVisible(true);
            });
        } else {
            SwingUtilities.invokeLater(() -> {
                SquashHawkeye app = new SquashHawkeye();
                app.setVisible(true);
            });
        }
    }
}
