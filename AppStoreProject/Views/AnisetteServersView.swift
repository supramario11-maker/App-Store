
import SwiftUI

struct AnisetteServer: Decodable, Identifiable {
    let name: String
    let address: String

    var id: String { address }
}

private struct ServerRegistry: Decodable {
    let servers: [AnisetteServer]
}

@MainActor
final class AnisetteServerManager: ObservableObject {
    @Published var servers: [AnisetteServer] = []
    @Published var statuses: [String: String] = [:]
    @Published var selectedServer: AnisetteServer?
    @Published var isChecking = false
    @Published var message = "Load the registry to begin."

    // Official SideStore registry.
    private let registryURL = URL(
        string: "https://servers.sidestore.io/servers.json"
    )!

    func loadRegistry() async {
        message = "Loading registry..."

        do {
            var request = URLRequest(url: registryURL)
            request.timeoutInterval = 15

            let (data, response) = try await URLSession.shared.data(
                for: request
            )

            guard let http = response as? HTTPURLResponse,
                  (200..<300).contains(http.statusCode) else {
                message = "Registry request failed."
                return
            }

            let registry = try JSONDecoder().decode(
                ServerRegistry.self,
                from: data
            )

            servers = registry.servers.filter {
                URL(string: $0.address)?.scheme == "https"
            }

            message = "Loaded \(servers.count) HTTPS endpoints."
        } catch {
            message = "Could not load registry: \(error.localizedDescription)"
        }
    }

    func checkServers() async {
        guard !servers.isEmpty else {
            message = "Load the registry first."
            return
        }

        isChecking = true
        selectedServer = nil
        statuses = [:]
        message = "Checking configured endpoints..."

        for server in servers {
            guard let url = URL(string: server.address) else {
                statuses[server.id] = "Invalid URL"
                continue
            }

            var request = URLRequest(url: url)
            request.httpMethod = "GET"
            request.timeoutInterval = 8

            do {
                let (_, response) = try await URLSession.shared.data(
                    for: request
                )

                guard let http = response as? HTTPURLResponse else {
                    statuses[server.id] = "Invalid response"
                    continue
                }

                if (200..<300).contains(http.statusCode) {
                    statuses[server.id] = "Reachable"

                    if selectedServer == nil {
                        selectedServer = server
                    }
                } else {
                    statuses[server.id] = "HTTP \(http.statusCode)"
                }
            } catch {
                statuses[server.id] = "Unavailable"
            }
        }

        isChecking = false

        if let selectedServer {
            message = "First reachable endpoint: \(selectedServer.name)"
        } else {
            message = "No configured endpoint responded successfully."
        }
    }
}

struct AnisetteServersView: View {
    @StateObject private var manager = AnisetteServerManager()

    var body: some View {
        NavigationView {
            List {
                Section("Registry") {
                    Text(manager.message)
                        .font(.subheadline)

                    Button("Load Official Registry") {
                        Task {
                            await manager.loadRegistry()
                        }
                    }

                    Button("Check Endpoints in Order") {
                        Task {
                            await manager.checkServers()
                        }
                    }
                    .disabled(manager.isChecking || manager.servers.isEmpty)

                    if manager.isChecking {
                        ProgressView("Checking servers...")
                    }
                }

                Section("Endpoints") {
                    ForEach(manager.servers) { server in
                        VStack(alignment: .leading, spacing: 5) {
                            HStack {
                                Text(server.name)
                                    .font(.headline)

                                Spacer()

                                if manager.selectedServer?.id == server.id {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.green)
                                }
                            }

                            Text(server.address)
                                .font(.caption)
                                .foregroundColor(.secondary)

                            Text(manager.statuses[server.id] ?? "Not checked")
                                .font(.caption)
                        }
                        .padding(.vertical, 4)
                    }
                }

                Section {
                    Text(
                        "Reachability does not verify Anisette protocol compatibility, security, or signing success. Only use services you trust."
                    )
                    .font(.footnote)
                    .foregroundColor(.secondary)
                }
            }
            .navigationTitle("Anisette Services")
        }
    }
}
