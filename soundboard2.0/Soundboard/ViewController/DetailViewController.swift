//
//  DetailViewController.swift
//  Soundboard
//
//  Created by Dominic Henze on 24.09.19.
//  Copyright © 2019 Dominic Henze. All rights reserved.
//

import UIKit
import AVFoundation

class DetailViewController: UIViewController {
    
    struct Constants {
        static let CollectionCellIdentifier = "CollectionCell"
        static let ErrorMsg = "Matze sagt: Geht nicht!"
        static let ButtonUnit = "sec"
        
        static let ButtonAmount = 3
        
        static let ButtonPadding: CGFloat = 16
        static let ButtonTitleTextSize: CGFloat = 50
        static let ButtonCornerRadius: CGFloat = 10
        static let TitleTextSize: CGFloat = 25
        static let CalculatedWidthDefaultValue: CGFloat = 100
    }
    
    @IBOutlet weak var collectionView: UICollectionView!
    
    var player: AVAudioPlayer?
    var timer: Timer?
    var currentSelectedButton: UIButton?
    var calculatedWidth = Constants.CalculatedWidthDefaultValue
    
    var detailItem: SoundObject? {
        didSet {
            configureView()
        }
    }

    func configureView() {
        if let detail = detailItem {
            self.title = detail.name
        }
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        
        configureView()
        
        self.navigationController?.navigationBar.barTintColor = Config.Detail.Color.barColor
        self.navigationController?.navigationBar.titleTextAttributes = [NSAttributedString.Key.foregroundColor: Config.Detail.Color.barTextColor, NSAttributedString.Key.font: UIFont.boldSystemFont(ofSize: Constants.TitleTextSize)]
        
        collectionView.backgroundColor = Config.Detail.Color.backgroundColor
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        
        player?.stop()
        timer?.invalidate()
    }
    
    @objc func buttonClick(button: UIButton) {
        currentSelectedButton?.highlighted(false)
        timer?.invalidate()
        
        if currentSelectedButton != nil && button == currentSelectedButton {
            player?.stop()
            currentSelectedButton = nil
            return
        }
        
        currentSelectedButton = button
        currentSelectedButton?.highlighted(true)
        
        let secondsToPlay = Double(button.tag)
        
        do {
            player = try AVAudioPlayer(contentsOf: detailItem!.fileURL)
            player?.delegate = self
            player?.play()
            timer = Timer.scheduledTimer(withTimeInterval: secondsToPlay, repeats: false) { _ in
                self.player?.stop()
                self.currentSelectedButton?.highlighted(false)
                self.currentSelectedButton = nil
            }
        } catch {
            print(Constants.ErrorMsg)
        }
    }
    
    func calculateButtonWidthAndHeight(parentViewWidth: CGFloat, itemAmount: Int) -> CGFloat {
        let totalPaddingSpace = 2 * Constants.ButtonPadding * CGFloat(itemAmount + 1)
        let availableWidth = parentViewWidth - CGFloat(totalPaddingSpace)
        let widthPerItem = availableWidth / CGFloat(itemAmount)
        
        return widthPerItem
    }
}

extension DetailViewController: AVAudioPlayerDelegate {
    func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        timer?.invalidate()
        currentSelectedButton?.highlighted(false)
        currentSelectedButton = nil
    }
}

extension DetailViewController: UICollectionViewDataSource {
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        return Config.buttonTimeArrayInSeconds.count
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        let cell = collectionView.dequeueReusableCell(withReuseIdentifier: Constants.CollectionCellIdentifier, for: indexPath)
        let button = UIButton(frame: CGRect(x: 0, y: 0, width: calculatedWidth, height: calculatedWidth))
        
        button.setTitle("\(Config.buttonTimeArrayInSeconds[indexPath.row]) \(Constants.ButtonUnit)", for: .normal)
        button.titleLabel?.font = UIFont.systemFont(ofSize: Constants.ButtonTitleTextSize, weight: .bold)
        button.backgroundColor = Config.Detail.Color.buttonColor
        button.layer.cornerRadius = Constants.ButtonCornerRadius
        button.tag = Config.buttonTimeArrayInSeconds[indexPath.row]
        
        if Config.Detail.Layout.buttonHasBorder {
            button.layer.borderWidth = CGFloat(Config.Detail.Layout.buttonBorderWidth)
            button.layer.borderColor = Config.Detail.Color.buttonBorderColor.cgColor
        }
        
        button.addTarget(self, action: #selector(buttonClick), for: .touchUpInside)
        
        cell.backgroundColor = Config.Detail.Color.backgroundColor
        cell.addSubview(button)
        
        return cell
    }
}

extension DetailViewController: UICollectionViewDelegateFlowLayout {
    func collectionView(_ collectionView: UICollectionView, layout collectionViewLayout: UICollectionViewLayout, sizeForItemAt indexPath: IndexPath) -> CGSize {
        calculatedWidth = calculateButtonWidthAndHeight(parentViewWidth: self.view.frame.size.width, itemAmount: Constants.ButtonAmount)
        
        return CGSize(width: calculatedWidth, height: calculatedWidth)
    }

    func collectionView(_ collectionView: UICollectionView,
                        layout collectionViewLayout: UICollectionViewLayout,
                        insetForSectionAt section: Int) -> UIEdgeInsets {
        return UIEdgeInsets(top: Constants.ButtonPadding, left: Constants.ButtonPadding, bottom: Constants.ButtonPadding, right: Constants.ButtonPadding)
    }
    
    func collectionView(_ collectionView: UICollectionView, layout collectionViewLayout: UICollectionViewLayout, minimumLineSpacingForSectionAt section: Int) -> CGFloat {
        return Constants.ButtonPadding
    }
}
