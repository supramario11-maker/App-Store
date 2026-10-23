import SwiftUI
import UniformTypeIdentifiers

struct MainStoreView: View {
    @State private var availableApps: [AppItem] = [
        AppItem(id: UUID(), title: "Roblox", subtitle: "Play Millions of Games", version: "2.640.0", ipaURL: nil, iconName: "gamecontroller"),
        AppItem(id: UUID(), title: "Dr. Driving", subtitle: "Dr. Driving drives you crazy!", version: "1.69", ipaURL: nil, iconName: "car"),
        AppItem(id: UUID(), title: "Combat Master", subtitle: "Fast-Paced Action FPS", version: "0.12.3", ipaURL: nil, iconName: "shield")
    ]
    @State private var showFilePicker = false

    var body: some View {
        NavigationView {
            List(availableApps) { app in
                HStack(spacing: 16) {
                    Image(systemName: app.iconName)
                        .resizable()
                        .scaledToFit()
                        .frame(width: 40, height: 40)
                        .padding(10)
                        .background(Color(.systemGray5))
                        .cornerRadius(12)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(app.title).font(.headline)
                        Text(app.subtitle).font(.subheadline).foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Button("GET") {
                        print("Signing app package locally: \(app.title)")
                    }
                    .font(.system(size: 14, weight: .bold))
                    .padding(.horizontal, 20)
                    .padding(.vertical, 6)
                    .background(Color(.systemGroupedBackground))
                    .cornerRadius(20)
                }
            }
            .navigationTitle("Discover")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showFilePicker = true }) {
                        Image(systemName: "plus").font(.title2)
                    }
                }
            }
            .sheet(isPresented: $showFilePicker) {
                DocumentPicker(apps: $availableApps)
            }
        }
    }
}

struct DocumentPicker: UIViewControllerRepresentable {
    @Binding var apps: [AppItem]
    
    func makeUIViewController(context: Context) -> UIDocumentPickerViewController {
        let picker = UIDocumentPickerViewController(forOpeningContentTypes: [UTType(filenameExtension: "ipa")!])
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIDocumentPickerViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    
    class Coordinator: NSObject, UIDocumentPickerDelegate {
        var parent: DocumentPicker
        init(_ parent: DocumentPicker) { self.parent = parent }
        
        func documentPicker(_ controller: UIDocumentPickerViewController, didPickDocumentsAt urls: [URL]) {
            guard let url = urls.first else { return }
            let name = url.deletingPathExtension().lastPathComponent
            let newApp = AppItem(id: UUID(), title: name, subtitle: "Local Unsigned IPA", version: "1.0", ipaURL: url, iconName: "doc.badge.plus")
            parent.apps.append(newApp)
        }
    }
}
