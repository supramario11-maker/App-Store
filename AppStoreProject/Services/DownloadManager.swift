import Foundation

class DownloadManager: NSObject, ObservableObject, URLSessionDownloadDelegate {
    @Published var progress: Float = 0.0
    @Published var isDownloading = false
    @Published var downloadedFileUrl: URL?

    func downloadIPA(from url: URL) {
        isDownloading = true
        progress = 0.0
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: OperationQueue.main)
        let downloadTask = session.downloadTask(with: url)
        downloadTask.resume()
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didFinishDownloadingTo location: URL) {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask).first!
        let destinationURL = documentsURL.appendingPathComponent("downloaded_app.ipa")
        
        try? fileManager.removeItem(at: destinationURL)
        do {
            try fileManager.moveItem(at: location, to: destinationURL)
            self.downloadedFileUrl = destinationURL
        } catch {
            print("File save error: \(error.localizedDescription)")
        }
        isDownloading = false
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask, didWriteData bytesWritten: Int64, totalBytesWritten: Int64, totalBytesExpectedToWrite: Int64) {
        DispatchQueue.main.async {
            self.progress = Float(totalBytesWritten) / Float(totalBytesExpectedToWrite)
        }
    }
}
