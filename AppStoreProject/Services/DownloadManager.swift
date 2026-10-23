
import Foundation
import Combine

struct DownloadItem: Identifiable {
    let id = UUID()
    let title: String
    var progress: Double = 0
    var isDownloading = true
    var fileURL: URL?
    var error: String?
}

final class DownloadManager: NSObject, ObservableObject {

    @Published private(set) var downloads: [DownloadItem] = []

    private var session: URLSession!
    private var tasks: [Int: UUID] = [:]
    private var pendingDownloads: [UUID: String] = [:]

    override init() {
        super.init()

        let configuration = URLSessionConfiguration.default
        session = URLSession(
            configuration: configuration,
            delegate: self,
            delegateQueue: .main
        )
    }

    func downloadIPA(from url: URL, title: String) {
        guard url.scheme?.lowercased() == "https",
              url.host != nil else {
            addFailedDownload(
                title: title,
                message: "A valid HTTPS download URL is required."
            )
            return
        }

        let id = UUID()

        downloads.append(
            DownloadItem(id: id, title: title)
        )

        pendingDownloads[id] = title

        let task = session.downloadTask(with: url)
        tasks[task.taskIdentifier] = id
        task.resume()
    }

    func cancelDownload(id: UUID) {
        guard let entry = downloads.first(where: {
            $0.id == id
        }) else {
            return
        }

        for (taskID, downloadID) in tasks
        where downloadID == id {
            session.getAllTasks { tasks in
                tasks.first(where: {
                    $0.taskIdentifier == taskID
                })?.cancel()
            }
        }

        update(id) {
            $0.isDownloading = false
            $0.error = "Download cancelled."
        }

        pendingDownloads.removeValue(forKey: id)
    }

    private func update(
        _ id: UUID,
        _ change: (inout DownloadItem) -> Void
    ) {
        guard let index = downloads.firstIndex(
            where: { $0.id == id }
        ) else {
            return
        }

        change(&downloads[index])
    }

    private func addFailedDownload(
        title: String,
        message: String
    ) {
        var item = DownloadItem(
            title: title,
            isDownloading: false
        )
        item.error = message
        downloads.append(item)
    }

    private func saveFile(
        from location: URL,
        suggestedName: String,
        id: UUID
    ) throws -> URL {
        let documents = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        )[0]

        let safeName = URL(fileURLWithPath: suggestedName)
            .lastPathComponent

        let name = safeName.isEmpty
            ? "\(id.uuidString).ipa"
            : safeName

        let destination = documents.appendingPathComponent(name)

        // Avoid overwriting an existing download.
        let finalURL = documents.appendingPathComponent(
            "\(UUID().uuidString)-\(name)"
        )

        try FileManager.default.moveItem(
            at: location,
            to: finalURL
        )

        return finalURL
    }
}

extension DownloadManager: URLSessionDownloadDelegate {

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        guard let id = tasks[downloadTask.taskIdentifier],
              totalBytesExpectedToWrite > 0 else {
            return
        }

        let progress = min(
            1.0,
            Double(totalBytesWritten) /
                Double(totalBytesExpectedToWrite)
        )

        update(id) {
            $0.progress = progress
        }
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        guard let id = tasks[downloadTask.taskIdentifier] else {
            return
        }

        guard let response = downloadTask.response
                as? HTTPURLResponse,
              (200...299).contains(response.statusCode) else {
            update(id) {
                $0.isDownloading = false
                $0.error = "The server returned an unsuccessful response."
            }
            tasks.removeValue(
                forKey: downloadTask.taskIdentifier
            )
            return
        }

        do {
            let suggestedName =
                downloadTask.response?.suggestedFilename
                ?? "\(id.uuidString).ipa"

            let fileURL = try saveFile(
                from: location,
                suggestedName: suggestedName,
                id: id
            )

            update(id) {
                $0.progress = 1
                $0.isDownloading = false
                $0.fileURL = fileURL
            }
        } catch {
            update(id) {
                $0.isDownloading = false
                $0.error = error.localizedDescription
            }
        }

        tasks.removeValue(
            forKey: downloadTask.taskIdentifier
        )
        pendingDownloads.removeValue(forKey: id)
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: Error?
    ) {
        guard let id = tasks[task.taskIdentifier] else {
            return
        }

        if let error = error {
            update(id) {
                $0.isDownloading = false
                $0.error = error.localizedDescription
            }

            tasks.removeValue(forKey: task.taskIdentifier)
            pendingDownloads.removeValue(forKey: id)
        }
    }
}
