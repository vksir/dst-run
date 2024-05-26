package registry

import (
	"context"
	"dst-run/pkg/log"
	"fmt"
)

// TODO: RCU lock

var topicToSubscriberToCallback = make(map[string]map[string]any)

func Notify(ctx context.Context, topic string, msg any) {
	log.Info("notify: topic=%s, msg=%v", topic, msg)
	subscriberToCallback, ok := topicToSubscriberToCallback[topic]
	if ok {
		for subscriber, callback := range subscriberToCallback {
			switch callback.(type) {
			case chan any:
				select {
				case callback.(chan any) <- msg:
				case <-ctx.Done():
					log.Error("notify failed: topic=%s, subscriber=%s, msg=%v", topic, subscriber, msg)
				}
			case func(context.Context, any) error:
				if err := callback.(func(context.Context, any) error)(ctx, msg); err != nil {
					log.Error("notify failed: topic=%s, subscriber=%s, msg=%v, err=%v", topic, subscriber, msg, err)
				}
			default:
				log.Error("notify failed: topic=%s, subscriber=%s, msg=%v, err=invalid callback type %T",
					topic, subscriber, msg, callback)
			}
		}
	}
}

func Subscribe(topic, subscriber string, callback any) error {
	switch callback.(type) {
	case chan any:
	case func(context.Context, any) error:
	default:
		return fmt.Errorf("invalid callback type: %T", callback)
	}
	subscriberToCallback, ok := topicToSubscriberToCallback[topic]
	if !ok {
		subscriberToCallback = make(map[string]any)
		topicToSubscriberToCallback[topic] = subscriberToCallback
	}

	subscriberToCallback[subscriber] = callback
	log.Warn("subscribe success: topic=%s, subscriber=%s, callback_type=%T", topic, subscriber, callback)
	return nil
}

func Unsubscribe(topic, subscriber string) {
	subscriberToCallback, ok := topicToSubscriberToCallback[topic]
	if ok {
		if _, ok := subscriberToCallback[subscriber]; ok {
			delete(subscriberToCallback, subscriber)
		}
	}
	log.Warn("unsubscribe success: topic=%s, subscriber=%s", topic, subscriber)
}
